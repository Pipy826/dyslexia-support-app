<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">{{ article ? (article.content_type === 'video' ? '视频' : '文章') : '详情' }}</view>
      <view class="share-btn-header" @click="shareArticle">
        <text class="ph ph-share-network"></text>
      </view>
    </view>

    <scroll-view class="page-content" scroll-y v-if="article">
      <!-- 封面图 -->
      <view class="cover-section" v-if="article.cover_image">
        <image :src="article.cover_image" mode="aspectFill" class="cover-img" />
      </view>

      <!-- 视频播放区 -->
      <view class="video-section" v-if="article.content_type === 'video' && article.video_url">
        <video
          class="video-player"
          :src="article.video_url"
          controls
          :poster="article.cover_image || ''"
          object-fit="contain"
        ></video>
      </view>

      <!-- 文章内容区 -->
      <view class="content-section">
        <!-- 标签 -->
        <view class="tags-row" v-if="article.tags && article.tags.length">
          <text v-for="tag in article.tags" :key="tag" class="tag-chip">{{ tag }}</text>
        </view>

        <!-- 标题 -->
        <view class="article-title">{{ article.title }}</view>

        <!-- 元信息 -->
        <view class="article-meta">
          <view class="meta-author">
            <text class="ph ph-user-circle meta-icon"></text>
            {{ article.author }}
          </view>
          <view class="meta-views">
            <text class="ph ph-eye meta-icon"></text>
            {{ article.view_count }} 次阅读
          </view>
          <view class="meta-date" v-if="article.created_at">
            {{ formatDate(article.created_at) }}
          </view>
        </view>

        <view class="divider"></view>

        <!-- 摘要 -->
        <view class="article-summary" v-if="article.summary">
          {{ article.summary }}
        </view>

        <!-- 正文 -->
        <view class="article-body" v-if="article.content">
          <!-- H5 用 rich-text 渲染，小程序也支持 -->
          <rich-text :nodes="article.content"></rich-text>
        </view>

        <!-- 无内容提示 -->
        <view class="no-content" v-if="!article.content && !article.video_url">
          <text class="ph ph-info"></text>
          内容暂未发布，请稍后查看
        </view>
      </view>

      <!-- 底部推荐 -->
      <view class="recommend-section" v-if="relatedArticles.length > 0">
        <view class="recommend-title">相关推荐</view>
        <view
          v-for="item in relatedArticles"
          :key="item.id"
          class="recommend-card"
          @click="openArticle(item)"
        >
          <view class="recommend-type" :class="item.content_type">
            <text :class="item.content_type === 'video' ? 'ph ph-video' : 'ph ph-article'"></text>
          </view>
          <view class="recommend-info">
            <view class="recommend-title-text">{{ item.title }}</view>
            <view class="recommend-meta">{{ item.author }} · {{ item.view_count }} 次</view>
          </view>
        </view>
      </view>

      <view style="height: 60rpx;"></view>
    </scroll-view>

    <!-- 加载中 -->
    <view class="loading-state" v-if="loading">
      <text class="ph ph-circle-notch spin"></text>
      加载中...
    </view>
  </view>
</template>

<script>
import { getArticle, getArticles } from '../../../api/article.js'

export default {
  data() {
    return {
      articleId: null,
      article: null,
      relatedArticles: [],
      loading: true,
    }
  },
  onLoad(options) {
    this.articleId = parseInt(options.id)
    this.loadArticle()
  },
  methods: {
    async loadArticle() {
      this.loading = true
      try {
        this.article = await getArticle(this.articleId)
        // 加载相关推荐（同类型，排除当前）
        const res = await getArticles({
          content_type: this.article.content_type,
          page_size: 3,
        })
        this.relatedArticles = (res.items || []).filter(a => a.id !== this.articleId)
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    goBack() {
      uni.navigateBack()
    },
    shareArticle() {
      // #ifdef MP-WEIXIN
      uni.showShareMenu({ withShareTicket: true })
      // #endif
      // #ifdef H5
      if (typeof navigator !== 'undefined' && navigator.share) {
        navigator.share({
          title: this.article?.title || '读写科普',
          text: this.article?.summary || '',
          url: typeof window !== 'undefined' ? window.location.href : '',
        }).catch(() => {})
      } else {
        uni.showToast({ title: '链接已复制', icon: 'none' })
      }
      // #endif
    },
    openArticle(item) {
      uni.redirectTo({
        url: `/pages/parent/articles/detail?id=${item.id}`,
      })
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`
    },
  },
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #F5F7FA;
  display: flex;
  flex-direction: column;
}

/* 头部 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 30;
  background: rgba(255, 255, 255, 0.95);
  padding: 56rpx 24rpx 16rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 1rpx 0 rgba(0, 0, 0, 0.04);
}

.back-btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }

.header-title {
  flex: 1;
  font-size: 30rpx;
  font-weight: 700;
  color: #2D3748;
  text-align: center;
}

.share-btn-header {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.share-btn-header .ph { font-size: 28rpx; color: #718096; }

/* 内容区 */
.page-content { flex: 1; }

/* 封面 */
.cover-section {
  width: 100%;
  height: 360rpx;
  overflow: hidden;
}
.cover-img { width: 100%; height: 100%; }

/* 视频 */
.video-section {
  width: 100%;
  background: #000;
}
.video-player {
  width: 100%;
  height: 420rpx;
}

/* 内容区 */
.content-section {
  background: #FFFFFF;
  padding: 32rpx;
  margin-bottom: 16rpx;
}

.tags-row {
  display: flex;
  gap: 10rpx;
  flex-wrap: wrap;
  margin-bottom: 16rpx;
}

.tag-chip {
  font-size: 20rpx;
  font-weight: 600;
  color: #4F9EF8;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
}

.article-title {
  font-size: 36rpx;
  font-weight: 800;
  color: #2D3748;
  line-height: 1.4;
  margin-bottom: 20rpx;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 20rpx;
  flex-wrap: wrap;
  margin-bottom: 24rpx;
}

.meta-author, .meta-views, .meta-date {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #A0AEC0;
  font-weight: 500;
}

.meta-icon { font-size: 22rpx; }

.divider {
  height: 1rpx;
  background: #F0F0F0;
  margin-bottom: 24rpx;
}

.article-summary {
  font-size: 28rpx;
  color: #4A5568;
  line-height: 1.8;
  font-weight: 500;
  margin-bottom: 24rpx;
  padding: 20rpx 24rpx;
  background: linear-gradient(135deg, #F8FAFC, #F1F5F9);
  border-left: 6rpx solid #4F9EF8;
  border-radius: 0 12rpx 12rpx 0;
}

.article-body {
  font-size: 28rpx;
  color: #2D3748;
  line-height: 1.9;
  font-weight: 400;
}

.no-content {
  display: flex;
  align-items: center;
  gap: 10rpx;
  font-size: 24rpx;
  color: #A0AEC0;
  padding: 40rpx 0;
  justify-content: center;
}

.no-content .ph { font-size: 28rpx; }

/* 相关推荐 */
.recommend-section {
  background: #FFFFFF;
  padding: 24rpx 32rpx;
  margin-bottom: 16rpx;
}

.recommend-title {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
  margin-bottom: 16rpx;
}

.recommend-card {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #F5F5F5;
  transition: all 0.2s;
}

.recommend-card:last-child { border-bottom: none; }
.recommend-card:active { opacity: 0.7; }

.recommend-type {
  width: 52rpx; height: 52rpx;
  border-radius: 14rpx;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.recommend-type.article {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
}
.recommend-type.article .ph { font-size: 26rpx; color: #4F9EF8; }

.recommend-type.video {
  background: linear-gradient(135deg, #FFF7ED, #FFEDD5);
}
.recommend-type.video .ph { font-size: 26rpx; color: #F97316; }

.recommend-info { flex: 1; min-width: 0; }

.recommend-title-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #2D3748;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recommend-meta {
  font-size: 20rpx;
  color: #A0AEC0;
  margin-top: 4rpx;
  font-weight: 500;
}

/* 加载状态 */
.loading-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  font-size: 26rpx;
  color: #A0AEC0;
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.spin { animation: spin 0.8s linear infinite; display: inline-block; }
</style>
