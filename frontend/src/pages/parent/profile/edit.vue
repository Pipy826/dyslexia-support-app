<template>
  <view class="page-container">
    <!-- 返回按钮 -->
    <view class="back-btn" @click="goBack">
      <text class="ph ph-arrow-left"></text>
    </view>

    <!-- 标题区 -->
    <view class="header-section">
      <view class="page-title">{{ isEdit ? '编辑档案' : '创建儿童档案' }}</view>
      <view class="page-subtitle" v-if="!isEdit">为了推荐最精准的评估与训练计划，请完善信息。</view>
    </view>

    <!-- 极简表单 -->
    <view class="form-section">

      <!-- 头像选择 -->
      <view class="avatar-upload" @click="chooseAvatar">
        <view class="avatar-preview">
          <image v-if="formData.avatar_url" :src="getAvatarUrl(formData.avatar_url)" class="avatar-img" mode="aspectFill" />
          <text v-else class="ph ph-user"></text>
          <view class="camera-icon">
            <text class="ph ph-camera"></text>
          </view>
        </view>
        <view class="upload-hint">点击上传头像</view>
      </view>

      <!-- 姓名/昵称 -->
      <view class="input-group">
        <label class="input-label">孩子姓名 / 昵称</label>
        <view class="input-item">
          <input
            type="text"
            v-model="formData.name"
            placeholder="例如：小明"
            class="form-input"
          />
        </view>
      </view>

      <!-- 性别选择 -->
      <view class="input-group">
        <label class="input-label">性别</label>
        <view class="gender-grid">
          <view
            :class="['gender-option', { active: formData.gender === 'boy' }]"
            @click="formData.gender = 'boy'"
          >
            <text class="ph ph-gender-male"></text>
            <text class="gender-text">男孩</text>
          </view>
          <view
            :class="['gender-option', { active: formData.gender === 'girl' }]"
            @click="formData.gender = 'girl'"
          >
            <text class="ph ph-gender-female"></text>
            <text class="gender-text">女孩</text>
          </view>
        </view>
      </view>

      <!-- 年级阶段选择 -->
      <view class="input-group">
        <label class="input-label">当前年级阶段</label>
        <view class="grade-grid">
          <view
            v-for="item in gradeOptions"
            :key="item.value"
            :class="['grade-option', { active: formData.grade === item.value }]"
            @click="formData.grade = item.value"
          >
            {{ item.label }}
          </view>
        </view>
      </view>

      <!-- 是否发现困难 -->
      <view class="difficulty-notice" :class="{ checked: formData.hasDifficulty }">
        <view class="notice-checkbox" @click="formData.hasDifficulty = !formData.hasDifficulty">
          <text class="ph ph-check" v-if="formData.hasDifficulty"></text>
        </view>
        <view class="notice-text">
          我已经观察到孩子在识字、拼写或阅读方面存在一定的困难或抗拒情绪。（勾选后系统将调整筛查侧重点）
        </view>
      </view>

      <!-- 是否已有机构评估经历 -->
      <view class="difficulty-notice" :class="{ checked: formData.hasProfessionalEval }">
        <view class="notice-checkbox" @click="formData.hasProfessionalEval = !formData.hasProfessionalEval">
          <text class="ph ph-check" v-if="formData.hasProfessionalEval"></text>
        </view>
        <view class="notice-text">
          孩子曾在医院、康复机构或专业教育机构进行过相关评估或诊断。
        </view>
      </view>

    </view>

    <!-- 完成按钮 -->
    <button class="main-btn" @click="handleSave">
      {{ isEdit ? '保存修改' : '完成创建，进入首页' }}
    </button>
  </view>
</template>

<script>
import { createChild, updateChild, getChild } from '../../../api/child.js'
import { uploadAvatar, getAvatarUrl } from '../../../api/child.js'

export default {
  data() {
    return {
      childId: null,
      isEdit: false,
      uploading: false,
      formData: {
        name: '',
        gender: 'boy',
        grade: '一年级',
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
      ]
    }
  },
  onLoad(options) {
    if (options.id) {
      this.childId = parseInt(options.id)
      this.isEdit = true
      this.loadChild()
    }
  },
  methods: {
    async loadChild() {
      try {
        const child = await getChild(this.childId)
        this.formData = {
          name: child.name,
          gender: child.gender === 'female' ? 'girl' : 'boy',
          grade: child.grade || '1',
          hasDifficulty: child.has_difficulty || false,
          hasProfessionalEval: false,
          avatar_url: child.avatar_url || '',
          birth_date: child.birth_date || ''
        }
      } catch (e) {
        console.error('加载失败', e)
      }
    },
    goBack() {
      uni.navigateBack()
    },
    getAvatarUrl(path) {
      if (!path) return ''
      if (path.startsWith('http')) return path
      const base = import.meta.env.VITE_API_BASE_URL || ''
      return base + path
    },
    chooseAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          const filePath = res.tempFilePaths[0]
          this.uploading = true
          try {
            const result = await uploadAvatar(filePath)
            this.formData.avatar_url = result.url
            uni.showToast({ title: '头像上传成功', icon: 'success' })
          } catch (e) {
            uni.showToast({ title: '上传失败，请重试', icon: 'none' })
          } finally {
            this.uploading = false
          }
        }
      })
    },
    async handleSave() {
      if (!this.formData.name) {
        uni.showToast({ title: '请输入孩子姓名或昵称', icon: 'none' })
        return
      }

      try {
        // 编辑时需要保留原有 birth_date，新建时用年级推算
        let birthDate = this.formData.birth_date
        if (!birthDate) {
          const gradeAgeMap = { '幼儿园': 5, '一年级': 7, '二年级': 8, '三年级': 9, '四年级': 10, '五年级': 11 }
          const age = gradeAgeMap[this.formData.grade] || 8
          const birthYear = new Date().getFullYear() - age
          birthDate = `${birthYear}-06-01`
        }

        const data = {
          name: this.formData.name,
          gender: this.formData.gender === 'girl' ? 'female' : 'male',
          birth_date: birthDate,
          grade: this.formData.grade,
          has_difficulty: this.formData.hasDifficulty,
          avatar_url: this.formData.avatar_url || null
        }

        if (this.isEdit) {
          await updateChild(this.childId, data)
          uni.showToast({ title: '保存成功', icon: 'success' })
        } else {
          await createChild(data)
          uni.showToast({ title: '创建成功', icon: 'success' })
        }

        setTimeout(() => {
          if (this.isEdit) {
            uni.navigateBack()
          } else {
            uni.reLaunch({ url: '/pages/parent/home/index' })
          }
        }, 1000)
      } catch (e) {
        uni.showToast({ title: this.isEdit ? '保存失败' : '创建失败', icon: 'none' })
      }
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #FFFFFF;
  padding: 96rpx 48rpx 80rpx;
}

/* 返回按钮 */
.back-btn {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: #F9FAFB;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 48rpx;
}

.back-btn .ph {
  font-size: 36rpx;
  color: #6B7280;
}

/* 标题区 */
.header-section {
  margin-bottom: 64rpx;
}

.page-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #374151;
  margin-bottom: 16rpx;
}

.page-subtitle {
  font-size: 28rpx;
  color: #6B7280;
}

/* 表单 */
.form-section {
  display: flex;
  flex-direction: column;
  gap: 48rpx;
  margin-bottom: 64rpx;
}

/* 头像上传 */
.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16rpx;
}

.avatar-preview {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: #EFF6FF;
  border: 4rpx solid #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
  position: relative;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.avatar-preview .ph {
  font-size: 64rpx;
  color: #3B82F6;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.camera-icon {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  background: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.camera-icon .ph {
  font-size: 24rpx;
  color: #3B82F6;
}

.upload-hint {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 输入组 */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.input-label {
  font-size: 28rpx;
  font-weight: 700;
  color: #374151;
  padding-left: 8rpx;
}

.input-item {
  background: #F9FAFB;
  border: 2rpx solid #F3F4F6;
  border-radius: 32rpx;
  padding: 28rpx 32rpx;
  transition: all 0.3s;
}

.input-item:focus-within {
  border-color: #3B82F6;
  background: #FFFFFF;
}

.form-input {
  width: 100%;
  font-size: 28rpx;
  color: #374151;
  background: transparent;
}

.form-input::placeholder {
  color: #9CA3AF;
}

/* 性别选择 */
.gender-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24rpx;
}

.gender-option {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 28rpx;
  background: #F9FAFB;
  border: 2rpx solid #F3F4F6;
  border-radius: 32rpx;
  transition: all 0.3s;
}

.gender-option .ph {
  font-size: 36rpx;
  color: #9CA3AF;
}

.gender-text {
  font-size: 28rpx;
  font-weight: 500;
  color: #6B7280;
}

.gender-option.active {
  background: #EFF6FF;
  border-color: #3B82F6;
}

.gender-option.active .ph {
  color: #3B82F6;
}

.gender-option.active .gender-text {
  color: #3B82F6;
}

/* 年级选择 */
.grade-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24rpx;
}

.grade-option {
  padding: 24rpx 16rpx;
  background: #F9FAFB;
  border: 2rpx solid #F3F4F6;
  border-radius: 24rpx;
  text-align: center;
  font-size: 24rpx;
  font-weight: 500;
  color: #6B7280;
  transition: all 0.3s;
}

.grade-option.active {
  background: #EFF6FF;
  border-color: #3B82F6;
  color: #3B82F6;
  font-weight: 700;
}

/* 困难提示 */
.difficulty-notice {
  background: #EFF6FF;
  border: 2rpx solid #DBEAFE;
  border-radius: 32rpx;
  padding: 32rpx;
  display: flex;
  gap: 24rpx;
  align-items: flex-start;
  margin-top: 16rpx;
}

.notice-checkbox {
  width: 32rpx;
  height: 32rpx;
  border-radius: 8rpx;
  border: 2rpx solid #D1D5DB;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 4rpx;
  transition: all 0.3s;
}

.difficulty-notice.checked .notice-checkbox {
  background: #3B82F6;
  border-color: #3B82F6;
}

.notice-checkbox .ph {
  font-size: 18rpx;
  color: #FFFFFF;
}

.notice-text {
  font-size: 24rpx;
  color: #6B7280;
  line-height: 1.6;
}

/* 主按钮 */
.main-btn {
  width: 100%;
  background: #3B82F6;
  color: #FFFFFF;
  border-radius: 32rpx;
  padding: 32rpx;
  font-size: 32rpx;
  font-weight: 700;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.3);
}

/* Toast */
.toast {
  position: fixed;
  top: 80rpx;
  left: 50%;
  transform: translateX(-50%) translateY(-20rpx);
  background: #374151;
  color: #FFFFFF;
  padding: 24rpx 48rpx;
  border-radius: 50rpx;
  font-size: 26rpx;
  font-weight: 500;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.2);
  opacity: 0;
  transition: all 0.3s;
  pointer-events: none;
  z-index: 9999;
}

.toast.show {
  opacity: 1;
  transform: translateX(-50%) translateY(0);
}
</style>
