<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">隐私政策</view>
    </view>
    <scroll-view class="page-content" scroll-y>
      <view class="doc-title">儿童读写障碍智能筛查与干预系统隐私政策</view>
      <view class="doc-date">更新日期：2024年1月1日</view>

      <view class="section">
        <view class="section-title">一、我们收集的信息</view>
        <view class="section-body">
          <view class="item">• 账号信息：手机号、用户名（用于账号管理）</view>
          <view class="item">• 儿童档案：姓名/昵称、性别、年龄、年级（用于匹配适龄题目）</view>
          <view class="item">• 行为数据：游戏过程中的答题记录、反应时间、操作轨迹（用于能力评估）</view>
          <view class="item">• 设备信息：设备型号、操作系统版本（用于优化体验）</view>
        </view>
      </view>

      <view class="section">
        <view class="section-title">二、信息使用目的</view>
        <view class="section-body">
          <view class="item">• 提供儿童读写能力筛查与评估服务</view>
          <view class="item">• 生成个性化训练建议和报告</view>
          <view class="item">• 改善产品功能和用户体验</view>
          <view class="item">• 保障账号安全</view>
        </view>
      </view>

      <view class="section">
        <view class="section-title">三、儿童数据特别保护</view>
        <view class="section-body">我们严格遵守《儿童个人信息网络保护规定》。儿童行为数据仅用于本产品内的能力评估，不会对外共享、出售或用于任何商业广告目的。我们不会在未经家长同意的情况下收集儿童的个人信息。</view>
      </view>

      <view class="section">
        <view class="section-title">四、信息共享</view>
        <view class="section-body">我们不会将您的个人信息出售给第三方。仅在以下情况下可能共享：法律法规要求、保护用户安全、经您明确同意。AI 分析服务使用加密传输，不包含可识别个人身份的信息。</view>
      </view>

      <view class="section">
        <view class="section-title">五、数据存储与安全</view>
        <view class="section-body">您的数据存储在安全的服务器上，采用加密传输和存储。我们定期进行安全审计，防止数据泄露。</view>
      </view>

      <view class="section">
        <view class="section-title">六、您的权利</view>
        <view class="section-body">
          <view class="item">• 查阅权：您可随时查看账号和孩子的所有数据</view>
          <view class="item">• 更正权：您可修改不准确的信息</view>
          <view class="item">• 删除权：您可申请删除账号及所有相关数据</view>
          <view class="item">• 撤回同意：您可随时撤回对数据处理的同意</view>
        </view>
      </view>

      <view class="section">
        <view class="section-title">七、联系我们</view>
        <view class="section-body">如有隐私相关问题，请通过应用内"联系客服"功能联系我们，我们将在15个工作日内回复。</view>
      </view>

      <view style="height: 80rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  methods: {
    goBack() { uni.navigateBack() }
  }
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
.page-content { padding: 32rpx; width: 100%; box-sizing: border-box; }
.doc-title { font-size: 32rpx; font-weight: 800; color: #2D3748; margin-bottom: 8rpx; line-height: 1.5; }
.doc-date { font-size: 22rpx; color: #A0AEC0; margin-bottom: 32rpx; }
.section { margin-bottom: 28rpx; }
.section-title { font-size: 28rpx; font-weight: 700; color: #2D3748; margin-bottom: 12rpx; }
.section-body { font-size: 26rpx; color: #718096; line-height: 1.8; font-weight: 500; }
.item { margin-bottom: 8rpx; }
</style>
