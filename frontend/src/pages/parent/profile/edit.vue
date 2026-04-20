<template>
  <view class="page-container">
    <view class="page-header">
      <view class="back-btn" @click="goBack">
        <text class="ph ph-arrow-left"></text>
      </view>
      <view class="header-title">{{ isEdit ? '编辑档案' : '创建儿童档案' }}</view>
    </view>

    <scroll-view class="page-content" scroll-y>
      <!-- 头像 -->
      <view class="avatar-section" @click="chooseAvatar">
        <view class="avatar-wrap">
          <image v-if="formData.avatar_url" :src="getAvatarUrl(formData.avatar_url)" class="avatar-img" mode="aspectFill" />
          <text v-else class="ph ph-user avatar-icon"></text>
          <view class="camera-badge"><text class="ph ph-camera"></text></view>
        </view>
        <view class="avatar-hint">点击更换头像</view>
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

      <!-- 出生年份 -->
      <view class="section-title">出生年份</view>
      <view class="tag-grid">
        <view
          v-for="y in birthYearOptions"
          :key="y"
          :class="['tag-option', { active: formData.birth_year === y }]"
          @click="formData.birth_year = y"
        >{{ y }}年</view>
      </view>

      <!-- 出生月份 -->
      <view class="section-title">出生月份</view>
      <view class="tag-grid">
        <view
          v-for="m in 12"
          :key="m"
          :class="['tag-option', { active: formData.birth_month === m }]"
          @click="formData.birth_month = m"
        >{{ m }}月</view>
      </view>

      <!-- 出生日期 -->
      <view class="section-title">出生日期</view>
      <view class="tag-grid">
        <view
          v-for="d in daysInMonth"
          :key="d"
          :class="['tag-option', { active: formData.birth_day === d }]"
          @click="formData.birth_day = d"
        >{{ d }}日</view>
      </view>

      <!-- 附加信息 -->
      <view class="section-title">附加信息（选填）</view>
      <view class="check-card" :class="{ checked: formData.hasDifficulty }" @click="formData.hasDifficulty = !formData.hasDifficulty">
        <view class="check-box">
          <text class="ph ph-check" v-if="formData.hasDifficulty"></text>
        </view>
        <view class="check-text">已观察到孩子在识字、拼写或阅读方面存在困难（勾选后系统将调整筛查侧重点）</view>
      </view>
      <view class="check-card" :class="{ checked: formData.hasProfessionalEval }" @click="formData.hasProfessionalEval = !formData.hasProfessionalEval">
        <view class="check-box">
          <text class="ph ph-check" v-if="formData.hasProfessionalEval"></text>
        </view>
        <view class="check-text">孩子曾在医院或专业机构进行过相关评估或诊断</view>
      </view>

      <view style="height: 40rpx;"></view>
    </scroll-view>

    <view class="bottom-bar">
      <button class="submit-btn" @click="handleSave">
        {{ isEdit ? '保存修改' : '完成创建，进入首页' }}
      </button>
    </view>
  </view>
</template>

<script>
import { createChild, updateChild, getChild } from '../../../api/child.js'
import { uploadAvatar } from '../../../api/child.js'

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
        birth_year: new Date().getFullYear() - 7,
        birth_month: 6,
        birth_day: 15,
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
  computed: {
    birthYearOptions() {
      const currentYear = new Date().getFullYear()
      const years = []
      for (let age = 3; age <= 13; age++) {
        years.push(currentYear - age)
      }
      return years
    },
    daysInMonth() {
      const days = new Date(this.formData.birth_year, this.formData.birth_month, 0).getDate()
      return Array.from({ length: days }, (_, i) => i + 1)
    }
  },
  watch: {
    'formData.birth_month'(newMonth) {
      const maxDay = new Date(this.formData.birth_year, newMonth, 0).getDate()
      if (this.formData.birth_day > maxDay) this.formData.birth_day = maxDay
    },
    'formData.birth_year'(newYear) {
      const maxDay = new Date(newYear, this.formData.birth_month, 0).getDate()
      if (this.formData.birth_day > maxDay) this.formData.birth_day = maxDay
    }
  },
  onLoad(options) {
    if (options.id || options.child_id) {
      this.childId = parseInt(options.id || options.child_id)
      this.isEdit = true
      this.loadChild()
    }
  },
  methods: {
    async loadChild() {
      try {
        const child = await getChild(this.childId)
        const parts = (child.birth_date || '').split('-')
        this.formData = {
          name: child.name,
          gender: child.gender === 'female' ? 'girl' : 'boy',
          grade: child.grade || '一年级',
          birth_year: parts[0] ? parseInt(parts[0]) : new Date().getFullYear() - 7,
          birth_month: parts[1] ? parseInt(parts[1]) : 6,
          birth_day: parts[2] ? parseInt(parts[2]) : 15,
          hasDifficulty: child.has_difficulty || false,
          hasProfessionalEval: child.has_professional_eval || false,
          avatar_url: child.avatar_url || ''
        }
      } catch (e) {
        uni.showToast({ title: '加载失败', icon: 'none' })
      }
    },
    goBack() { uni.navigateBack() },
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
          this.uploading = true
          try {
            const result = await uploadAvatar(res.tempFilePaths[0])
            this.formData.avatar_url = result.url
            uni.showToast({ title: '头像上传成功', icon: 'success' })
          } catch (e) {
            uni.showToast({ title: '上传失败', icon: 'none' })
          } finally {
            this.uploading = false
          }
        }
      })
    },
    async handleSave() {
      if (!this.formData.name) {
        uni.showToast({ title: '请输入孩子姓名', icon: 'none' })
        return
      }
      try {
        const data = {
          name: this.formData.name,
          gender: this.formData.gender === 'girl' ? 'female' : 'male',
          birth_date: `${this.formData.birth_year}-${String(this.formData.birth_month).padStart(2,'0')}-${String(this.formData.birth_day).padStart(2,'0')}`,
          grade: this.formData.grade,
          has_difficulty: this.formData.hasDifficulty,
          has_professional_eval: this.formData.hasProfessionalEval,
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
          this.isEdit ? uni.navigateBack() : uni.reLaunch({ url: '/pages/parent/home/index' })
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
  background: #F5F7FA;
  overflow-x: hidden;
  padding-bottom: 160rpx;
}

.page-header {
  position: sticky; top: 0; z-index: 30;
  background: rgba(255,255,255,0.95); padding: 56rpx 24rpx 16rpx;
  display: flex; align-items: center; box-shadow: 0 1rpx 0 rgba(0,0,0,0.04);
}
.back-btn {
  width: 56rpx; height: 56rpx; border-radius: 14rpx; background: #F5F5F5;
  display: flex; align-items: center; justify-content: center; margin-right: 16rpx;
}
.back-btn .ph { font-size: 28rpx; color: #718096; }
.header-title { font-size: 30rpx; font-weight: 700; color: #2D3748; }

.page-content { padding: 24rpx 32rpx; width: 100%; box-sizing: border-box; }

.avatar-section {
  display: flex; flex-direction: column; align-items: center; padding: 32rpx 0 24rpx;
}
.avatar-wrap {
  width: 140rpx; height: 140rpx; border-radius: 50%;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  display: flex; align-items: center; justify-content: center;
  position: relative; margin-bottom: 16rpx;
  box-shadow: 0 4rpx 16rpx rgba(79,158,248,0.2); overflow: hidden;
}
.avatar-img { width: 100%; height: 100%; border-radius: 50%; }
.avatar-icon { font-size: 64rpx; color: #4F9EF8; }
.camera-badge {
  position: absolute; bottom: 4rpx; right: 4rpx;
  width: 44rpx; height: 44rpx; border-radius: 50%;
  background: #4F9EF8; display: flex; align-items: center; justify-content: center;
}
.camera-badge .ph { font-size: 22rpx; color: #FFFFFF; }
.avatar-hint { font-size: 22rpx; color: #A0AEC0; font-weight: 500; }

.form-card {
  background: #FFFFFF; border-radius: 24rpx; overflow: hidden;
  margin-bottom: 24rpx; box-shadow: 0 2rpx 16rpx rgba(0,0,0,0.04);
}
.form-row { padding: 24rpx 28rpx; }
.form-label { font-size: 22rpx; color: #A0AEC0; font-weight: 600; margin-bottom: 10rpx; }
.form-input { width: 100%; font-size: 30rpx; font-weight: 700; color: #2D3748; background: transparent; }

.section-title { font-size: 26rpx; font-weight: 700; color: #718096; margin-bottom: 14rpx; }

.gender-row { display: flex; gap: 16rpx; margin-bottom: 24rpx; }
.gender-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 10rpx;
  padding: 24rpx; background: #FFFFFF; border: 2rpx solid #E5E7EB;
  border-radius: 20rpx; font-size: 26rpx; font-weight: 700; color: #718096;
  transition: all 0.2s; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.gender-btn .ph { font-size: 30rpx; }
.gender-btn.active { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border-color: #4F9EF8; color: #4F9EF8; }

.tag-grid { display: flex; flex-wrap: wrap; gap: 12rpx; margin-bottom: 24rpx; }
.tag-option {
  padding: 14rpx 20rpx; background: #FFFFFF; border: 2rpx solid #E5E7EB;
  border-radius: 14rpx; font-size: 24rpx; font-weight: 600; color: #718096;
  transition: all 0.2s; box-shadow: 0 1rpx 4rpx rgba(0,0,0,0.04);
}
.tag-option.active { background: linear-gradient(135deg, #EFF6FF, #DBEAFE); border-color: #4F9EF8; color: #4F9EF8; }

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

.bottom-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  padding: 20rpx 32rpx calc(20rpx + env(safe-area-inset-bottom));
  background: rgba(255,255,255,0.95); box-shadow: 0 -1rpx 0 rgba(0,0,0,0.06);
}
.submit-btn {
  width: 100%; background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF;
  border-radius: 20rpx; padding: 28rpx; font-size: 30rpx; font-weight: 700;
  box-shadow: 0 4rpx 16rpx rgba(59,130,246,0.3);
}
</style>
