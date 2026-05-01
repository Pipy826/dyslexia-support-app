<template>
  <view class="date-picker-wheel">
    <picker-view
      class="picker-view"
      :value="pickerValue"
      @change="onPickerChange"
      indicator-style="height: 88rpx;"
    >
      <!-- 年列 -->
      <picker-view-column>
        <view class="picker-item" v-for="year in yearList" :key="year">{{ year }}年</view>
      </picker-view-column>
      <!-- 月列 -->
      <picker-view-column>
        <view class="picker-item" v-for="month in monthList" :key="month">{{ month }}月</view>
      </picker-view-column>
      <!-- 日列 -->
      <picker-view-column>
        <view class="picker-item" v-for="day in dayList" :key="day">{{ day }}日</view>
      </picker-view-column>
    </picker-view>

    <!-- 实时年龄标签 -->
    <view class="age-tag" v-if="ageDisplay">
      <text class="ph ph-cake"></text>
      <text class="age-text">{{ ageDisplay }}</text>
    </view>
  </view>
</template>

<script>
/**
 * DatePickerWheel — 三列联动滚轮日期选择器
 *
 * 正确性属性：
 * - 属性1：getDaysInMonth 月份天数计算正确（含闰年）
 * - 属性2：calcAge 年龄计算不变量（months 在 [0,11]）
 * - 属性3：输出格式始终为 YYYY-MM-DD
 * - 属性4：年级推算默认年份在 [当前年份-15, 当前年份] 范围内
 */

/**
 * 计算某年某月的天数（处理闰年）
 * @param {number} year
 * @param {number} month - 1-12
 * @returns {number} - 28/29/30/31
 */
export function getDaysInMonth(year, month) {
  return new Date(year, month, 0).getDate()
}

/**
 * 计算年龄
 * @param {string} birthDate - 'YYYY-MM-DD'
 * @returns {{ years: number, months: number }}
 */
export function calcAge(birthDate) {
  const birth = new Date(birthDate)
  const now = new Date()
  let years = now.getFullYear() - birth.getFullYear()
  let months = now.getMonth() - birth.getMonth()
  if (months < 0) {
    years--
    months += 12
  }
  if (now.getDate() < birth.getDate()) {
    months--
  }
  return { years: Math.max(0, years), months: Math.max(0, months) }
}

/**
 * 根据年级推算合理的默认出生年份
 * @param {string} grade
 * @param {number} currentYear
 * @returns {number}
 */
export function inferYearFromGrade(grade, currentYear) {
  const gradeAgeMap = {
    '学龄前': 5,
    '幼儿园': 5,
    '小学一年级': 7,
    '小学二年级': 8,
    '小学三年级': 9,
    '小学四年级': 10,
    '小学五年级': 11,
    '小学六年级': 12,
    '一年级': 7,
    '二年级': 8,
    '三年级': 9,
    '四年级': 10,
    '五年级': 11,
    '六年级': 12,
  }
  const age = gradeAgeMap[grade]
  if (age !== undefined) {
    const year = currentYear - age
    // 确保在合法范围内 [currentYear-15, currentYear]
    return Math.max(currentYear - 15, Math.min(currentYear, year))
  }
  // 默认：6岁
  return Math.max(currentYear - 15, currentYear - 6)
}

export default {
  name: 'DatePickerWheel',
  props: {
    modelValue: {
      type: String,
      default: '',
    },
    grade: {
      type: String,
      default: '',
    },
    maxDate: {
      type: String,
      default: '',
    },
    minDate: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue', 'change'],
  data() {
    const now = new Date()
    const currentYear = now.getFullYear()
    return {
      currentYear,
      selectedYear: currentYear - 6,
      selectedMonth: 1,
      selectedDay: 1,
    }
  },
  computed: {
    minYear() {
      if (this.minDate) {
        return parseInt(this.minDate.split('-')[0])
      }
      return this.currentYear - 15
    },
    maxYear() {
      if (this.maxDate) {
        return parseInt(this.maxDate.split('-')[0])
      }
      return this.currentYear
    },
    yearList() {
      const years = []
      for (let y = this.minYear; y <= this.maxYear; y++) {
        years.push(y)
      }
      return years
    },
    monthList() {
      const months = []
      for (let m = 1; m <= 12; m++) {
        months.push(m)
      }
      return months
    },
    dayList() {
      const maxDay = getDaysInMonth(this.selectedYear, this.selectedMonth)
      const days = []
      for (let d = 1; d <= maxDay; d++) {
        days.push(d)
      }
      return days
    },
    pickerValue() {
      const yearIdx = this.yearList.indexOf(this.selectedYear)
      const monthIdx = this.selectedMonth - 1
      const dayIdx = this.selectedDay - 1
      return [
        Math.max(0, yearIdx),
        Math.max(0, monthIdx),
        Math.max(0, dayIdx),
      ]
    },
    currentDateStr() {
      const y = this.selectedYear
      const m = String(this.selectedMonth).padStart(2, '0')
      const d = String(this.selectedDay).padStart(2, '0')
      return `${y}-${m}-${d}`
    },
    ageDisplay() {
      try {
        const { years, months } = calcAge(this.currentDateStr)
        if (years < 0) return ''
        if (years === 0 && months === 0) return '不足1个月'
        if (years === 0) return `${months}个月`
        if (months === 0) return `${years}岁`
        return `${years}岁${months}个月`
      } catch (e) {
        return ''
      }
    },
  },
  watch: {
    modelValue: {
      immediate: true,
      handler(val) {
        if (val && /^\d{4}-\d{2}-\d{2}$/.test(val)) {
          const parts = val.split('-')
          this.selectedYear = parseInt(parts[0])
          this.selectedMonth = parseInt(parts[1])
          this.selectedDay = parseInt(parts[2])
        } else {
          this.initDefault()
        }
      },
    },
    grade(val) {
      if (!this.modelValue) {
        this.initDefault()
      }
    },
    // 月份变化时修正日期
    selectedMonth(newMonth) {
      const maxDay = getDaysInMonth(this.selectedYear, newMonth)
      if (this.selectedDay > maxDay) {
        this.selectedDay = maxDay
      }
    },
    selectedYear(newYear) {
      const maxDay = getDaysInMonth(newYear, this.selectedMonth)
      if (this.selectedDay > maxDay) {
        this.selectedDay = maxDay
      }
    },
  },
  mounted() {
    if (!this.modelValue) {
      this.initDefault()
    }
  },
  methods: {
    initDefault() {
      const defaultYear = this.grade
        ? inferYearFromGrade(this.grade, this.currentYear)
        : this.currentYear - 6
      // 确保在合法范围内
      this.selectedYear = Math.max(this.minYear, Math.min(this.maxYear, defaultYear))
      this.selectedMonth = 1
      this.selectedDay = 1
      this.emitValue()
    },
    onPickerChange(e) {
      const [yearIdx, monthIdx, dayIdx] = e.detail.value
      this.selectedYear = this.yearList[yearIdx] || this.selectedYear
      this.selectedMonth = monthIdx + 1
      // 修正日期不超过当月最大天数
      const maxDay = getDaysInMonth(this.selectedYear, this.selectedMonth)
      this.selectedDay = Math.min(dayIdx + 1, maxDay)
      this.emitValue()
    },
    emitValue() {
      const dateStr = this.currentDateStr
      this.$emit('update:modelValue', dateStr)
      try {
        const age = calcAge(dateStr)
        this.$emit('change', { date: dateStr, age })
      } catch (e) {
        this.$emit('change', { date: dateStr, age: { years: 0, months: 0 } })
      }
    },
  },
}
</script>

<style scoped>
.date-picker-wheel {
  width: 100%;
}

.picker-view {
  width: 100%;
  height: 264rpx; /* 3行 × 88rpx */
  background: rgba(59, 130, 246, 0.03);
  border-radius: 20rpx;
  border: 2rpx solid #DBEAFE;
}

.picker-item {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  font-weight: 700;
  color: #2D3748;
  line-height: 88rpx;
}

/* 年龄标签 */
.age-tag {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  margin-top: 16rpx;
  padding: 8rpx 24rpx;
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 2rpx solid #BFDBFE;
  border-radius: 9999rpx;
  font-size: 24rpx;
  font-weight: 700;
  color: #3B82F6;
}

.age-tag .ph {
  font-size: 24rpx;
}
</style>
