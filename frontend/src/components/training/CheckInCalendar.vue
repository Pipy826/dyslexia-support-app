<template>
  <view class="check-in-calendar">
    <!-- 顶部连续天数展示 -->
    <view class="streak-header">
      <view class="streak-info">
        <text v-if="streakCount >= 3" class="streak-flame">🔥</text>
        <text class="streak-count">{{ streakCount }}</text>
        <text class="streak-label">天连续打卡</text>
      </view>
      <view class="month-nav">
        <text class="month-text">{{ currentYear }}年{{ currentMonth + 1 }}月</text>
      </view>
    </view>

    <!-- 星期标题行 -->
    <view class="weekday-row">
      <view
        v-for="day in weekdays"
        :key="day"
        class="weekday-cell"
      >
        <text class="weekday-text">{{ day }}</text>
      </view>
    </view>

    <!-- 日历格子 -->
    <view class="calendar-grid">
      <!-- 月初空白占位 -->
      <view
        v-for="n in firstDayOfMonth"
        :key="'empty-' + n"
        class="day-cell empty"
      ></view>

      <!-- 日期格子 -->
      <view
        v-for="day in daysInMonth"
        :key="day"
        :class="[
          'day-cell',
          isToday(day) ? 'today' : '',
          isCheckedIn(day) ? 'checked-in' : '',
        ]"
      >
        <view class="day-inner">
          <text v-if="isCheckedIn(day)" class="day-star">⭐</text>
          <text v-else class="day-number" :class="isToday(day) ? 'today-number' : ''">{{ day }}</text>
        </view>
      </view>
    </view>

    <!-- 底部说明 -->
    <view class="legend">
      <view class="legend-item">
        <text class="legend-icon">⭐</text>
        <text class="legend-text">已打卡</text>
      </view>
      <view class="legend-item" v-if="streakCount >= 3">
        <text class="legend-icon">🔥</text>
        <text class="legend-text">连续{{ streakCount }}天</text>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  name: 'CheckInCalendar',
  props: {
    // 已打卡日期数组，格式 "YYYY-MM-DD"
    checkInDates: {
      type: Array,
      default: () => [],
    },
    // 连续打卡天数
    streakCount: {
      type: Number,
      default: 0,
    },
  },
  data() {
    const now = new Date()
    return {
      currentYear: now.getFullYear(),
      currentMonth: now.getMonth(), // 0-indexed
      weekdays: ['一', '二', '三', '四', '五', '六', '日'],
    }
  },
  computed: {
    // 当月天数
    daysInMonth() {
      return new Date(this.currentYear, this.currentMonth + 1, 0).getDate()
    },
    // 当月第一天是星期几（0=周日，转换为周一起始：0→6, 1→0, ..., 6→5）
    firstDayOfMonth() {
      const d = new Date(this.currentYear, this.currentMonth, 1).getDay()
      // 转换为周一起始（0=周一, 6=周日）
      return d === 0 ? 6 : d - 1
    },
    // 将 checkInDates 转为 Set，方便快速查找
    checkedInSet() {
      const set = new Set()
      for (const dateStr of this.checkInDates) {
        // 只保留当月的日期
        const d = new Date(dateStr)
        if (d.getFullYear() === this.currentYear && d.getMonth() === this.currentMonth) {
          set.add(d.getDate())
        }
      }
      return set
    },
  },
  methods: {
    isToday(day) {
      const now = new Date()
      return (
        now.getFullYear() === this.currentYear &&
        now.getMonth() === this.currentMonth &&
        now.getDate() === day
      )
    },
    isCheckedIn(day) {
      return this.checkedInSet.has(day)
    },
  },
}
</script>

<style scoped>
.check-in-calendar {
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 32rpx;
  box-shadow: 0 2rpx 16rpx rgba(0, 0, 0, 0.04);
}

/* 顶部连续天数 */
.streak-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.streak-info {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.streak-flame {
  font-size: 40rpx;
}

.streak-count {
  font-size: 48rpx;
  font-weight: 800;
  color: #F57F17;
  line-height: 1;
}

.streak-label {
  font-size: 24rpx;
  color: #718096;
  font-weight: 600;
}

.month-text {
  font-size: 26rpx;
  font-weight: 700;
  color: #2D3748;
}

/* 星期标题行 */
.weekday-row {
  display: flex;
  margin-bottom: 8rpx;
}

.weekday-cell {
  flex: 1;
  text-align: center;
  padding: 8rpx 0;
}

.weekday-text {
  font-size: 20rpx;
  color: #A0AEC0;
  font-weight: 600;
}

/* 日历格子 */
.calendar-grid {
  display: flex;
  flex-wrap: wrap;
}

.day-cell {
  width: calc(100% / 7);
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4rpx;
  box-sizing: border-box;
}

.day-cell.empty {
  /* 空白占位 */
}

.day-inner {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.day-cell.today .day-inner {
  background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
  border: 2rpx solid #4F9EF8;
}

.day-cell.checked-in .day-inner {
  background: linear-gradient(135deg, #FFFDE7, #FFF9C4);
}

.day-number {
  font-size: 24rpx;
  color: #4A5568;
  font-weight: 500;
}

.today-number {
  color: #4F9EF8;
  font-weight: 800;
}

.day-star {
  font-size: 28rpx;
  line-height: 1;
}

/* 底部说明 */
.legend {
  display: flex;
  gap: 32rpx;
  margin-top: 24rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #F0F0F0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.legend-icon {
  font-size: 24rpx;
}

.legend-text {
  font-size: 20rpx;
  color: #718096;
  font-weight: 500;
}
</style>
