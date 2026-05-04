<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">帮助中心</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 搜索框 -->
      <view class="search-wrap">
        <text class="ph ph-magnifying-glass search-icon"></text>
        <input class="search-input" v-model="searchText" placeholder="搜索常见问题..." />
      </view>

      <!-- 快捷入口 -->
      <view class="quick-grid">
        <view class="quick-item" v-for="item in quickItems" :key="item.title" @click="expandFaq(item.faqIndex)">
          <view class="quick-icon" :class="item.color">
            <text :class="'ph ' + item.icon"></text>
          </view>
          <view class="quick-label">{{ item.title }}</view>
        </view>
      </view>

      <!-- 常见问题 -->
      <view class="section-title">常见问题</view>
      <view class="faq-list">
        <view
          class="faq-item"
          v-for="(faq, i) in filteredFaqs"
          :key="i"
          @click="toggleFaq(i)"
        >
          <view class="faq-header">
            <view class="faq-q">{{ faq.q }}</view>
            <text :class="['ph', expandedIndex === i ? 'ph-caret-up' : 'ph-caret-down', 'faq-arrow']"></text>
          </view>
          <view class="faq-answer" v-if="expandedIndex === i">
            {{ faq.a }}
          </view>
        </view>
      </view>

      <!-- 联系客服 -->
      <view class="contact-card" @click="goToContact">
        <view class="contact-left">
          <view class="contact-icon">
            <text class="ph ph-headset"></text>
          </view>
          <view class="contact-info">
            <view class="contact-title">没找到答案？联系客服</view>
            <view class="contact-sub">工作日 9:00-18:00 在线</view>
          </view>
        </view>
        <text class="ph ph-arrow-right contact-arrow"></text>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
const FAQS = [
  { q: '游戏评估结果是医学诊断吗？', a: '不是。本产品的评估结果基于游戏化行为数据分析，仅供家庭参考，不构成任何医学诊断意见。如有疑虑，请咨询专业医疗机构。' },
  { q: '孩子的数据安全吗？', a: '我们高度重视儿童数据安全。儿童行为数据仅用于本产品内的能力评估，不会对外共享、出售或用于商业广告目的。您可随时申请删除孩子的所有数据。' },
  { q: '能力探索需要多长时间？', a: '每种游戏类型约需 5-10 分钟，建议在安静环境下完成。全部 9 种游戏类型完成后可获得综合能力图谱。' },
  { q: '"需要更多关注"意味着什么？', a: '"需要更多关注"不等于孩子"有问题"，而是提示某些能力维度需要重点关注和支持。读写学习特点与智力无关，通过科学训练可以显著改善。' },
  { q: '如何让孩子配合完成游戏？', a: '建议选择孩子状态好的时间段，以"玩游戏"的方式引导，不要强调"考试"。每次游戏时间不超过15分钟，避免疲劳。' },
  { q: '训练多久能看到效果？', a: '通常坚持每天 10-15 分钟的针对性训练，2-4 周后可以看到初步改善。建议完成训练后定期复评，跟踪变化趋势。' },
  { q: '可以同时管理多个孩子吗？', a: '可以。在"我的"页面点击"添加孩子"即可创建多个儿童档案，每个孩子的数据独立管理。' },
  { q: '忘记密码怎么办？', a: '在登录页面选择"验证码登录"，用手机号+验证码登录后，可在"我的"页面修改密码。' },
  { q: '如何删除账号？', a: '请通过"联系客服"功能提交账号删除申请，我们将在3个工作日内处理，删除后所有数据将无法恢复。' },
  { q: 'AI 问答有什么限制？', a: 'AI 助手专注于儿童读写能力相关问题，不提供医学诊断意见。对于需要更多关注的情况，AI 会建议寻求专业机构支持，而非给出确定性医疗判断。' },
]

export default {
  data() {
    return {
      searchText: '',
      expandedIndex: -1,
      quickItems: [
        { title: '探索说明', icon: 'ph-magnifying-glass', color: 'blue', faqIndex: 0 },
        { title: '数据安全', icon: 'ph-shield-check', color: 'green', faqIndex: 1 },
        { title: '训练指南', icon: 'ph-barbell', color: 'orange', faqIndex: 5 },
        { title: '账号问题', icon: 'ph-user', color: 'purple', faqIndex: 7 },
      ],
    }
  },
  computed: {
    filteredFaqs() {
      if (!this.searchText.trim()) return FAQS
      const kw = this.searchText.toLowerCase()
      return FAQS.filter(f => f.q.toLowerCase().includes(kw) || f.a.toLowerCase().includes(kw))
    },
  },
  methods: {
    toggleFaq(i) {
      this.expandedIndex = this.expandedIndex === i ? -1 : i
    },
    expandFaq(index) {
      this.expandedIndex = index
      // 滚动到对应位置
    },
    goToContact() {
      uni.navigateTo({ url: '/pages/parent/help/contact' })
    },
    goBack() { uni.navigateBack() },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: #F5F7FA; overflow-x: hidden; }
.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx;
  display: flex; align-items: center; box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.back-btn { width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5; display: flex; align-items: center; justify-content: center; margin-right: 16rpx; }
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }

.search-wrap {
  display: flex; align-items: center; background: #FFFFFF;
  border-radius: 20rpx; padding: 20rpx 24rpx; margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.04);
}
.search-icon { font-size: 28rpx; color: #A0AEC0; margin-right: 12rpx; }
.search-input { flex: 1; font-size: 26rpx; color: #2D3748; background: transparent; }

.quick-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16rpx; margin-bottom: 28rpx; }
.quick-item { display: flex; flex-direction: column; align-items: center; gap: 10rpx; }
.quick-item:active { opacity: 0.7; }
.quick-icon { width: 88rpx; height: 88rpx; border-radius: 22rpx; display: flex; align-items: center; justify-content: center; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.06); }
.quick-icon .ph { font-size: 36rpx; }
.quick-icon.blue { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); }
.quick-icon.blue .ph { color: #4F9EF8; }
.quick-icon.green { background: linear-gradient(135deg, #F0FDF4, #DCFCE7); }
.quick-icon.green .ph { color: #22C55E; }
.quick-icon.orange { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.quick-icon.orange .ph { color: #F57F17; }
.quick-icon.purple { background: linear-gradient(135deg, #F5F3FF, #EDE9FE); }
.quick-icon.purple .ph { color: #A78BFA; }
.quick-label { font-size: 20rpx; color: #718096; font-weight: 600; }

.section-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 16rpx; }

.faq-list { display: flex; flex-direction: column; gap: 12rpx; margin-bottom: 24rpx; }
.faq-item { background: #FFFFFF; border-radius: 20rpx; overflow: hidden; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.faq-header { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 28rpx; }
.faq-q { flex: 1; font-size: 26rpx; font-weight: 700; color: #2D3748; line-height: 1.5; }
.faq-arrow { font-size: 24rpx; color: #A0AEC0; flex-shrink: 0; margin-left: 12rpx; }
.faq-answer { padding: 0 28rpx 24rpx; font-size: 24rpx; color: #718096; line-height: 1.8; font-weight: 500; border-top: 1rpx solid #F5F5F5; padding-top: 16rpx; }

.contact-card {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border-radius: 20rpx; padding: 24rpx 28rpx;
  display: flex; align-items: center; justify-content: space-between;
  border: 1rpx solid #BFDBFE;
}
.contact-card:active { opacity: 0.8; }
.contact-left { display: flex; align-items: center; gap: 16rpx; }
.contact-icon { width: 64rpx; height: 64rpx; border-radius: 16rpx; background: #4F9EF8; display: flex; align-items: center; justify-content: center; }
.contact-icon .ph { font-size: 30rpx; color: #FFFFFF; }
.contact-title { font-size: 26rpx; font-weight: 700; color: #2D3748; }
.contact-sub { font-size: 20rpx; color: #718096; margin-top: 4rpx; }
.contact-arrow { font-size: 28rpx; color: #4F9EF8; }
</style>
