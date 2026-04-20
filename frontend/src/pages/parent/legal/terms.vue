<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">用户服务协议</view>
    </view>
    <scroll-view class="page-content" scroll-y>
      <view class="doc-title">儿童读写障碍智能筛查与干预系统用户服务协议</view>
      <view class="doc-date">更新日期：2024年1月1日</view>

      <view class="section">
        <view class="section-title">一、服务说明</view>
        <view class="section-body">本产品（"悦读小灯塔"）是一款面向家庭场景的儿童读写能力智能筛查与干预支持工具。本产品不是医疗诊断工具，筛查结果仅供家庭参考，不构成任何医学诊断意见。</view>
      </view>

      <view class="section">
        <view class="section-title">二、用户资格</view>
        <view class="section-body">本产品面向18周岁及以上的成年家长用户。注册账号即表示您确认具备完全民事行为能力，并同意代表您的家庭使用本产品。</view>
      </view>

      <view class="section">
        <view class="section-title">三、账号与安全</view>
        <view class="section-body">您有责任妥善保管账号信息，不得将账号转让或共享给他人。如发现账号被盗用，请立即联系我们。</view>
      </view>

      <view class="section">
        <view class="section-title">四、儿童数据保护</view>
        <view class="section-body">我们高度重视儿童数据安全。儿童的行为数据仅用于本产品内的能力评估，不会对外共享、出售或用于商业广告目的。您可随时申请删除孩子的所有数据。</view>
      </view>

      <view class="section">
        <view class="section-title">五、免责声明</view>
        <view class="section-body">本产品的筛查结果基于游戏化行为数据分析，存在一定误差范围。高风险结果不等于医学诊断，低风险结果也不排除存在问题的可能性。如有疑虑，请咨询专业医疗机构。</view>
      </view>

      <view class="section">
        <view class="section-title">六、服务变更</view>
        <view class="section-body">我们保留在合理通知后修改或终止服务的权利。重大变更将通过应用内通知告知用户。</view>
      </view>

      <view class="section">
        <view class="section-title">七、联系我们</view>
        <view class="section-body">如有任何问题，请通过应用内"联系客服"功能与我们联系。</view>
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
</style>
