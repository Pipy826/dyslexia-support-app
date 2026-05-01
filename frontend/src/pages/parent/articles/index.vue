<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="header-title">读写科普</view>
      <view class="header-sub">了解读写障碍，科学陪伴孩子</view>
    </view>

    <!-- 分类筛选 -->
    <view class="filter-bar">
      <view
        v-for="tab in tabs"
        :key="tab.value"
        :class="['filter-tab', { active: activeTab === tab.value }]"
        @click="switchTab(tab.value)"
      >
        <text :class="tab.icon"></text>
        {{ tab.label }}
      </view>
    </view>

    <scroll-view class="page-content" scroll-y @scrolltolower="loadMore">
      <!-- 置顶推荐 -->
      <view v-if="featuredItems.length > 0 && activeTab === 'all'" class="featured-section">
        <view class="section-label">
          <text class="ph ph-star-fill section-label-icon"></text>
          推荐阅读
        </view>
        <view
          v-for="item in featuredItems"
          :key="'f' + item.id"
          class="featured-card"
          @click="openArticle(item)"
        >
          <view class="featured-cover" v-if="item.cover_image">
            <image :src="item.cover_image" mode="aspectFill" class="cover-img" />
            <view class="video-badge" v-if="item.content_type === 'video'">
              <text class="ph ph-play-circle"></text> 视频
            </view>
          </view>
          <view class="featured-cover featured-cover-placeholder" v-else>
            <text :class="item.content_type === 'video' ? 'ph ph-video' : 'ph ph-article'"></text>
            <view class="video-badge" v-if="item.content_type === 'video'">
              <text class="ph ph-play-circle"></text> 视频
            </view>
          </view>
          <view class="featured-info">
            <view class="featured-title">{{ item.title }}</view>
            <view class="featured-summary" v-if="item.summary">{{ item.summary }}</view>
            <view class="featured-meta">
              <text class="meta-author">{{ item.author }}</text>
              <text class="meta-dot">·</text>
              <text class="meta-views">{{ item.view_count }} 次阅读</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 文章列表 -->
      <view class="section-label" v-if="activeTab === 'all' && featuredItems.length > 0">
        <text class="ph ph-list section-label-icon"></text>
        全部内容
      </view>

      <view v-if="articles.length > 0">
        <view
          v-for="item in articles"
          :key="item.id"
          class="article-card"
          @click="openArticle(item)"
        >
          <!-- 视频类型 -->
          <view v-if="item.content_type === 'video'" class="article-video-wrap">
            <view class="article-cover" v-if="item.cover_image">
              <image :src="item.cover_image" mode="aspectFill" class="cover-img-sm" />
              <view class="play-overlay">
                <text class="ph ph-play-circle play-icon"></text>
              </view>
            </view>
            <view class="article-cover article-cover-placeholder" v-else>
              <text class="ph ph-video placeholder-icon"></text>
              <view class="play-overlay">
                <text class="ph ph-play-circle play-icon"></text>
              </view>
            </view>
            <view class="article-info">
              <view class="article-type-badge video-badge-sm">视频</view>
              <view class="article-title">{{ item.title }}</view>
              <view class="article-meta">
                <text class="meta-author">{{ item.author }}</text>
                <text class="meta-dot">·</text>
                <text class="meta-views">{{ item.view_count }} 次</text>
              </view>
            </view>
          </view>

          <!-- 图文类型 -->
          <view v-else class="article-text-wrap">
            <view class="article-info-full">
              <view class="article-tags" v-if="item.tags && item.tags.length">
                <text
                  v-for="tag in item.tags.slice(0, 2)"
                  :key="tag"
                  class="tag-chip"
                >{{ tag }}</text>
              </view>
              <view class="article-title">{{ item.title }}</view>
              <view class="article-summary" v-if="item.summary">{{ item.summary }}</view>
              <view class="article-meta">
                <text class="meta-author">{{ item.author }}</text>
                <text class="meta-dot">·</text>
                <text class="meta-views">{{ item.view_count }} 次阅读</text>
              </view>
            </view>
            <view class="article-thumb" v-if="item.cover_image">
              <image :src="item.cover_image" mode="aspectFill" class="thumb-img" />
            </view>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view class="empty-state" v-if="!loading && articles.length === 0 && featuredItems.length === 0">
        <text class="ph ph-newspaper empty-icon"></text>
        <view class="empty-text">暂无科普内容</view>
        <view class="empty-hint">内容正在整理中，敬请期待</view>
      </view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="loading">
        <text class="ph ph-circle-notch spin"></text> 加载中...
      </view>
      <view class="no-more" v-if="!loading && noMore && articles.length > 0">
        已经到底了
      </view>

      <view style="height: 40rpx;"></view>
    </scroll-view>

    <!-- 底部导航栏 -->
    <tab-bar type="parent" current="/pages/parent/articles/index"></tab-bar>
  </view>
</template>

<script>
import { getArticles } from '../../../api/article.js'
import TabBar from '../../../components/tab-bar/index.vue'

export default {
  components: { TabBar },
  data() {
    return {
      activeTab: 'all',
      tabs: [
        { label: '全部', value: 'all', icon: 'ph ph-squares-four' },
        { label: '图文', value: 'article', icon: 'ph ph-article' },
        { label: '视频', value: 'video', icon: 'ph ph-video' },
      ],
      featuredItems: [],
      articles: [],
      page: 1,
      pageSize: 10,
      total: 0,
      loading: false,
      noMore: false,
    }
  },
  onShow() {
    this.resetAndLoad()
  },
  methods: {
    async resetAndLoad() {
      this.articles = []
      this.featuredItems = []
      this.page = 1
      this.noMore = false
      await this.loadFeatured()
      await this.loadArticles()
    },
    async loadFeatured() {
      if (this.activeTab !== 'all') return
      try {
        const res = await getArticles({ featured_only: true, page_size: 3 })
        this.featuredItems = res.items || []
      } catch (e) {
        this.featuredItems = []
      }
    },
    async loadArticles() {
      if (this.loading || this.noMore) return
      this.loading = true
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize,
        }
        if (this.activeTab !== 'all') {
          params.content_type = this.activeTab
        }
        const res = await getArticles(params)
        const items = res.items || []
        this.total = res.total || 0
        this.articles = this.page === 1 ? items : [...this.articles, ...items]
        if (this.articles.length >= this.total) {
          this.noMore = true
        }
      } catch (e) {
        console.error('加载文章失败', e)
      } finally {
        this.loading = false
      }
    },
    loadMore() {
      if (this.noMore || this.loading) return
      this.page++
      this.loadArticles()
    },
    switchTab(tab) {
      if (this.activeTab === tab) return
      this.activeTab = tab
      this.resetAndLoad()
    },
    openArticle(item) {
      uni.navigateTo({
        url: `/pages/parent/articles/detail?id=${item.id}`,
      })
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  padding-bottom: 160rpx;
  display: flex;
  flex-direction: column;
}

/* 头部 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 32rpx 16rpx;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.header-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
}

.header-sub {
  font-size: 22rpx;
  color: #A0AEC0;
  margin-top: 4rpx;
  font-weight: 500;
}

/* 分类筛选 */
.filter-bar {
  display: flex;
  gap: 12rpx;
  padding: 16rpx 32rpx;
  background: #FFFFFF;
  border-bottom: 1rpx solid #F0F0F0;
  flex-shrink: 0;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 10rpx 24rpx;
  border-radius: 9999rpx;
  font-size: 24rpx;
  font-weight: 600;
  color: #718096;
  background: #F5F7FA;
  transition: all 0.2s;
}

.filter-tab .ph { font-size: 24rpx; }

.filter-tab.active {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
}

/* 内容区 */
.page-content {
  flex: 1;
  padding: 20rpx 32rpx;
  box-sizing: border-box;
}

/* 区域标签 */
.section-label {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #718096;
  margin-bottom: 16rpx;
  margin-top: 8rpx;
}

.section-label-icon {
  font-size: 22rpx;
  color: #F57F17;
}

/* 置顶推荐卡片 */
.featured-section { margin-bottom: 8rpx; }

.featured-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.featured-card:active { transform: scale(0.99); }

.featured-cover {
  width: 100%;
  height: 280rpx;
  position: relative;
  overflow: hidden;
}

.featured-cover-placeholder {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex;
  align-items: center;
  justify-content: center;
}

.featured-cover-placeholder .ph {
  font-size: 80rpx;
  color: #93C5FD;
}

.cover-img { width: 100%; height: 100%; }

.video-badge {
  position: absolute;
  top: 16rpx;
  left: 16rpx;
  background: rgba(0, 0, 0, 0.6);
  color: #FFFFFF;
  font-size: 20rpx;
  font-weight: 700;
  padding: 6rpx 16rpx;
  border-radius: 9999rpx;
  display: flex;
  align-items: center;
  gap: 6rpx;
}

.video-badge .ph { font-size: 20rpx; }

.featured-info { padding: 20rpx 24rpx; }

.featured-title {
  font-size: 30rpx;
  font-weight: 800;
  color: #2D3748;
  margin-bottom: 8rpx;
  line-height: 1.4;
}

.featured-summary {
  font-size: 24rpx;
  color: #718096;
  line-height: 1.6;
  margin-bottom: 12rpx;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.featured-meta {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

/* 普通文章卡片 */
.article-card {
  background: #FFFFFF;
  border-radius: 20rpx;
  padding: 20rpx 24rpx;
  margin-bottom: 12rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.03);
  transition: all 0.2s;
}

.article-card:active { transform: scale(0.99); }

/* 视频类型布局 */
.article-video-wrap {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
}

.article-cover {
  width: 160rpx;
  height: 120rpx;
  border-radius: 12rpx;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}

.article-cover-placeholder {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon { font-size: 48rpx; color: #93C5FD; }

.cover-img-sm { width: 100%; height: 100%; }

.play-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}

.play-icon { font-size: 48rpx; color: #FFFFFF; }

.article-info { flex: 1; min-width: 0; }

.article-type-badge {
  display: inline-block;
  font-size: 18rpx;
  font-weight: 700;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
  margin-bottom: 8rpx;
}

.video-badge-sm {
  background: linear-gradient(135deg, #FFF7ED, #FFEDD5);
  color: #F97316;
}

/* 图文类型布局 */
.article-text-wrap {
  display: flex;
  gap: 16rpx;
  align-items: flex-start;
}

.article-info-full { flex: 1; min-width: 0; }

.article-thumb {
  width: 140rpx;
  height: 100rpx;
  border-radius: 12rpx;
  overflow: hidden;
  flex-shrink: 0;
}

.thumb-img { width: 100%; height: 100%; }

.article-tags {
  display: flex;
  gap: 8rpx;
  margin-bottom: 8rpx;
  flex-wrap: wrap;
}

.tag-chip {
  font-size: 18rpx;
  font-weight: 600;
  color: #4F9EF8;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
}

.article-title {
  font-size: 28rpx;
  font-weight: 700;
  color: #2D3748;
  line-height: 1.4;
  margin-bottom: 6rpx;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-summary {
  font-size: 22rpx;
  color: #A0AEC0;
  line-height: 1.5;
  margin-bottom: 8rpx;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.meta-author, .meta-views {
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 500;
}

.meta-dot { font-size: 20rpx; color: #D1D5DB; }

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 40rpx;
  opacity: 0.6;
}

.empty-icon { font-size: 80rpx; color: #D1D5DB; margin-bottom: 20rpx; }
.empty-text { font-size: 28rpx; color: #A0AEC0; font-weight: 600; }
.empty-hint { font-size: 22rpx; color: #D1D5DB; margin-top: 8rpx; font-weight: 500; }

/* 加载更多 */
.load-more, .no-more {
  text-align: center;
  font-size: 22rpx;
  color: #A0AEC0;
  padding: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; display: inline-block; }
</style>
