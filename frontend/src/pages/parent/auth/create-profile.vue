<template>
  <view class="page-container">
    <!-- 头部 -->
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">创建儿童档案</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 头像选择 -->
      <view class="avatar-section" @click="chooseAvatar">
        <view class="avatar-wrap">
          <image v-if="formData.avatar_url" :src="formData.avatar_url" class="avatar-img" mode="aspectFill" />
          <text v-else class="ph ph-user avatar-icon"></text>
          <view class="camera-badge"><text class="ph ph-camera"></text></view>
        </view>
        <view class="avatar-hint">{{ uploading ? '上传中...' : '点击上传头像（选填）' }}</view>
      </view>

      <!-- 姓名 -->
      <view class="form-card">
        <view class="form-row">
          <view class="form-label">孩子姓名 / 昵称</view>
          <input class="form-input" type="text" v-model="formData.name" placeholder="例如：小明" />
        </view>
      </view>

      <!-- 性别 -->
      <view class="section-title">性别</view>
      <view class="gender-row">
        <view :class="['gender-btn', { active: formData.gender === 'boy' }]" @click="formData.gender = 'boy'">
          <text class="ph ph-gender-male"></text> 男孩
        </view>
        <view :class="['gender-btn', { active: formData.gender === 'girl' }]" @click="formData.gender = 'girl'">
          <text class="ph ph-gender-female"></text> 女孩
        </view>
      </view>

      <!-- 年级 -->
      <view class="section-title">当前年级</view>
      <view class="tag-grid">
        <view
          v-for="item in gradeOptions"
          :key="item.value"
          :class="['tag-option', { active: formData.grade === item.value }]"
          @click="formData.grade = item.value"
        >{{ item.label }}</view>
      </view>

      <!-- 出生日期 -->
      <view class="section-title">出生日期</view>
      <view class="date-picker-wrap">
        <date-picker-wheel
          v-if="pickerReady"
          v-model="formData.birth_date"
          :grade="formData.grade"
          @change="onBirthDateChange"
        ></date-picker-wheel>
      </view>

      <!-- 附加信息 -->
      <view class="section-title">附加信息（选填）</view>
      <view class="check-card" :class="{ checked: formData.hasDifficulty }" @click="formData.hasDifficulty = !formData.hasDifficulty">
        <view class="check-box">
          <text class="ph ph-check" v-if="formData.hasDifficulty"></text>
        </view>
        <view class="check-text">已观察到孩子在识字、拼写或阅读方面存在困难（勾选后系统将调整能力探索侧重点）</view>
      </view>
      <view class="check-card" :class="{ checked: formData.hasProfessionalEval }" @click="formData.hasProfessionalEval = !formData.hasProfessionalEval">
        <view class="check-box">
          <text class="ph ph-check" v-if="formData.hasProfessionalEval"></text>
        </view>
        <view class="check-text">孩子曾在医院或专业机构进行过相关评估或诊断</view>
      </view>

      <!-- 底部按钮（放在 scroll-view 内部，避免遮挡问题） -->
      <view class="bottom-bar">
        <button class="submit-btn" @click="handleFinish" :disabled="uploading || submitting">
          <text v-if="submitting">创建中...</text>
          <text v-else>完成创建，进入首页</text>
        </button>
      </view>

      <view style="height: env(safe-area-inset-bottom); min-height: 20rpx;"></view>
    </scroll-view>
  </view>
</template>

<script>
import { createChild } from '../../../api/child.js'
import { setCurrentChild } from '../../../utils/auth.js'
import { uploadAvatar, getAvatarUrl } from '../../../api/child.js'
import DatePickerWheel from '../../../components/date-picker/DatePickerWheel.vue'

export default {
  components: { DatePickerWheel },
  data() {
    const now = new Date()
    const defaultYear = now.getFullYear() - 7
    return {
      formData: {
        name: '',
        gender: 'boy',
        grade: '一年级',
        birth_date: `${defaultYear}-06-15`,
        hasDifficulty: false,
        hasProfessionalEval: false,
        avatar_url: ''
      },
      gradeOptions: [
        { label: '学龄前', value: '幼儿园' },
        { label: '一年级', value: '一年级' },
        { label: '二年级', value: '二年级' },
        { label: '三年级', value: '三年级' },
        { label: '四年级', value: '四年级' },
        { label: '五/六年级', value: '五年级' }
      ],
      uploading: false,
      submitting: false,
      pickerReady: false,
    }
  },
  mounted() {
    // 延迟渲染 picker-view，等 scroll-view 的 DOM 完全就绪后再挂载
    // 避免 H5 模式下 ResizeSensor 读取 offsetWidth 时 DOM 还未准备好
    this.$nextTick(() => {
      setTimeout(() => {
        this.pickerReady = true
      }, 100)
    })
  },
  computed: {},
  watch: {},
  methods: {
    goBack() {
      uni.navigateBack()
    },
    onBirthDateChange({ date, age }) {
      this.formData.birth_date = date
    },
    chooseAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          this.uploading = true
          try {
            const result = await uploadAvatar(res.tempFilePaths[0])
            this.formData.avatar_url = result.url
          } catch (e) {
            uni.showToast({ title: '上传失败', icon: 'none' })
          } finally {
            this.uploading = false
          }
        }
      })
    },
    async handleFinish() {
      if (!this.formData.name) {
        uni.showToast({ title: '请输入孩子姓名或昵称', icon: 'none' })
        return
      }
      if (this.submitting) return
      this.submitting = true
      try {
        const child = await createChild({
          name: this.formData.name,
          gender: this.formData.gender === 'girl' ? 'female' : 'male',
          birth_date: this.formData.birth_date,
          grade: this.formData.grade,
          has_difficulty: this.formData.hasDifficulty,
          has_professional_eval: this.formData.hasProfessionalEval,
          avatar_url: this.formData.avatar_url || null
        })
        setCurrentChild(child)
        uni.showToast({ title: '创建成功', icon: 'success' })
        setTimeout(() => {
          const onboardingDone = uni.getStorageSync('onboarding_completed')
          if (!onboardingDone) {
            uni.reLaunch({ url: '/pages/parent/onboarding/index' })
          } else {
            uni.reLaunch({ url: '/pages/parent/home/index' })
          }
        }, 1000)
      } catch (e) {
        uni.showToast({ title: '创建失败，请重试', icon: 'none' })
      } finally {
        this.submitting = false
      }
    }
  }
}
</script>

<style scoped>
.page-container {
  height: 100vh;
  background: #F5F7FA;
  overflow-x: hidden;
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
  display: flex; align-items: center; justify-content: center; margin-right: 16rpx;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }

/* 内容区 */
.page-content {
  flex: 1;
  padding: 24rpx 32rpx;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

/* 头像区 */
.avatar-section {
  display: flex; flex-direction: column; align-items: center;
  padding: 32rpx 0 24rpx;
}
.avatar-wrap {
  width: 140rpx; height: 140rpx; border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
  position: relative; margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(79, 158, 248, 0.2);
  overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }
.avatar-icon { font-size: 64rpx; color: #4F9EF8; }
.camera-badge {
  position: absolute; bottom: 4rpx; right: 4rpx;
  width: 44rpx; height: 44rpx; border-radius: 50%;
  background: #4F9EF8; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.15);
}
.camera-badge .ph { font-size: 22rpx; color: #FFFFFF; }
.avatar-hint { font-size: 22rpx; color: #A0AEC0; font-weight: 500; }

/* 姓名卡片 */
.form-card {
  background: #FFFFFF; border-radius: 24rpx; overflow: hidden;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
}
.form-row { padding: 24rpx 28rpx; }
.form-label { font-size: 22rpx; color: #A0AEC0; font-weight: 600; margin-bottom: 10rpx; }
.form-input { width: 100%; font-size: 30rpx; font-weight: 700; color: #2D3748; background: transparent; }

/* 区域标题 */
.section-title { font-size: 26rpx; font-weight: 700; color: #718096; margin-bottom: 14rpx; }

/* 性别 */
.gender-row { display: flex; gap: 16rpx; margin-bottom: 24rpx; }
.gender-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 10rpx;
  padding: 24rpx; background: #FFFFFF; border: 2rpx solid #E5E7EB;
  border-radius: 20rpx; font-size: 26rpx; font-weight: 700; color: #718096;
  transition: all 0.2s; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.gender-btn .ph { font-size: 30rpx; }
.gender-btn.active { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border-color: #4F9EF8; color: #4F9EF8; }

/* 标签网格（年级、年份、月份、日期） */
.tag-grid { display: flex; flex-wrap: wrap; gap: 12rpx; margin-bottom: 24rpx; }
.tag-option {
  padding: 14rpx 20rpx; background: #FFFFFF; border: 2rpx solid #E5E7EB;
  border-radius: 14rpx; font-size: 24rpx; font-weight: 600; color: #718096;
  transition: all 0.2s; box-shadow: 0 1rpx 4rpx rgba(0,0,0,0.04);
}
.tag-option.active { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border-color: #4F9EF8; color: #4F9EF8; }

/* 日期选择器包裹层，避免 picker 未渲染时高度塌陷 */
.date-picker-wrap {
  min-height: 300rpx;
  margin-bottom: 24rpx;
}

/* 勾选卡片 */
.check-card {
  background: #FFFFFF; border: 2rpx solid #E5E7EB; border-radius: 20rpx;
  padding: 24rpx 28rpx; display: flex; gap: 20rpx; align-items: flex-start;
  margin-bottom: 16rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); transition: all 0.2s;
}
.check-card.checked { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border-color: #4F9EF8; }
.check-box {
  width: 36rpx; height: 36rpx; border-radius: 10rpx; border: 2rpx solid #D1D5DB;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 2rpx;
}
.check-card.checked .check-box { background: #4F9EF8; border-color: #4F9EF8; }
.check-box .ph { font-size: 20rpx; color: #FFFFFF; }
.check-text { font-size: 24rpx; color: #718096; line-height: 1.6; font-weight: 500; }
.check-card.checked .check-text { color: #2D3748; }

/* 底部按钮栏 */
.bottom-bar {
  padding: 24rpx 0 8rpx;
}
.submit-btn {
  width: 100%; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 20rpx; padding: 28rpx; font-size: 30rpx; font-weight: 700;
  box-shadow: 0 4rpx 16rpx rgba(59, 130, 246, 0.3);
}
.submit-btn[disabled] { opacity: 0.6; }
</style>
