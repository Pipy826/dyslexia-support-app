<template>
  <view class="page-container">
    <view class="top-bar">
      <view class="title-area"><text class="game-title">翻牌记忆</text></view>
      <view class="top-stats">
        <view class="stat-chip">
          <text class="ph ph-cards"></text>
          <text class="stat-val">{{ flipCount }}</text>
        </view>
        <view class="stat-chip timer-chip" :class="{ warning: timeLeft <= 30 }">
          <text class="ph ph-timer"></text>
          <text class="stat-val">{{ timeLeft }}s</text>
        </view>
        <view class="exit-btn" @click="exitGame">
          <text class="ph ph-x"></text>
        </view>
      </view>
    </view>

    <scroll-view class="content-area" scroll-y>
      <view class="card-grid grid-4col">
        <flip-card
          v-for="card in cards"
          :key="card.id"
          :is-flipped="card.isFlipped"
          :is-matched="card.isMatched"
          :content="card.content"
          :disabled="isAnimating || card.isMatched || phase !== 'playing'"
          @click="onCardClick(card)"
        ></flip-card>
      </view>

      <view class="progress-bar-area">
        <view class="progress-label">
          <text class="ph ph-check-circle"></text>
          已配对 {{ matchedPairs }} / {{ totalPairs }} 对
        </view>
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: (matchedPairs / totalPairs * 100) + '%' }"></view>
        </view>
      </view>
      <view style="height: 60rpx;"></view>
    </scroll-view>

    <!-- 超时弹窗 -->
    <view class="overlay" v-if="showTimeout">
      <view class="modal-card timeout-card">
        <view class="modal-emoji">⏰</view>
        <view class="modal-title">时间到啦！</view>
        <view class="modal-desc">没关系，再试一次吧！</view>
        <button class="modal-btn btn-retry" @click="restartGame">再试一次</button>
        <button class="modal-btn btn-back" @click="goBack">返回</button>
      </view>
    </view>

    <!-- 退出确认弹窗 -->
    <view class="modal-overlay" v-if="showExitModal" @click="showExitModal = false">
      <view class="modal-content" @click.stop>
        <view class="modal-icon warning">
          <text class="ph ph-warning"></text>
        </view>
        <view class="modal-title">要休息一下吗？</view>
        <view class="modal-desc">当前进度不会保存哦，下次重新开始。</view>
        <button class="modal-btn outline" @click="doExit">退出游戏</button>
        <button class="modal-btn primary" @click="showExitModal = false">继续游戏</button>
      </view>
    </view>

    <!-- 结果弹窗 -->
    <view class="overlay" v-if="phase === 'result'">
      <view class="modal-card result-card">
        <view class="result-emoji">{{ starsEarned >= 3 ? '🏆' : starsEarned >= 2 ? '😊' : '🌟' }}</view>
        <view class="result-title">太棒了！</view>
        <view class="result-stars">
          <text v-for="i in 3" :key="i" :class="['result-star', { earned: i <= starsEarned }]">⭐</text>
        </view>
        <view class="result-stats">
          <view class="stat-item">
            <view class="stat-num">{{ flipCount }}</view>
            <view class="stat-label">翻牌次数</view>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <view class="stat-num">{{ totalPairs }}</view>
            <view class="stat-label">共几对</view>
          </view>
          <view class="stat-divider"></view>
          <view class="stat-item">
            <view class="stat-num">{{ elapsedSeconds }}s</view>
            <view class="stat-label">用时</view>
          </view>
        </view>
        <button class="modal-btn btn-finish" @click="finishGame">
          <text class="ph ph-check-circle"></text> 完成
        </button>
        <button class="modal-btn btn-retry-sm" @click="restartGame">再玩一次</button>
      </view>
    </view>
  </view>
</template>

<script>
import FlipCard from '../../../components/game/FlipCard.vue'
import AudioManager from '../../../utils/audio.js'
import { calcFlipCardStars } from '../../../utils/gameScoring.js'
import { buildFlipCardPayload, enqueueRecord } from '../../../utils/gameDataBuilder.js'
import { completeTask, createTask } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'

// 每个难度30对，每次随机抽10对
const LOCAL_DECKS = {
  // L1：相同汉字配对（认字练习）—— 30对
  L1: [
    { pair_id: 'L1_p01', card_a: { type: 'text', content: '山' }, card_b: { type: 'text', content: '山' } },
    { pair_id: 'L1_p02', card_a: { type: 'text', content: '水' }, card_b: { type: 'text', content: '水' } },
    { pair_id: 'L1_p03', card_a: { type: 'text', content: '日' }, card_b: { type: 'text', content: '日' } },
    { pair_id: 'L1_p04', card_a: { type: 'text', content: '月' }, card_b: { type: 'text', content: '月' } },
    { pair_id: 'L1_p05', card_a: { type: 'text', content: '火' }, card_b: { type: 'text', content: '火' } },
    { pair_id: 'L1_p06', card_a: { type: 'text', content: '木' }, card_b: { type: 'text', content: '木' } },
    { pair_id: 'L1_p07', card_a: { type: 'text', content: '土' }, card_b: { type: 'text', content: '土' } },
    { pair_id: 'L1_p08', card_a: { type: 'text', content: '金' }, card_b: { type: 'text', content: '金' } },
    { pair_id: 'L1_p09', card_a: { type: 'text', content: '风' }, card_b: { type: 'text', content: '风' } },
    { pair_id: 'L1_p10', card_a: { type: 'text', content: '云' }, card_b: { type: 'text', content: '云' } },
    { pair_id: 'L1_p11', card_a: { type: 'text', content: '花' }, card_b: { type: 'text', content: '花' } },
    { pair_id: 'L1_p12', card_a: { type: 'text', content: '草' }, card_b: { type: 'text', content: '草' } },
    { pair_id: 'L1_p13', card_a: { type: 'text', content: '鸟' }, card_b: { type: 'text', content: '鸟' } },
    { pair_id: 'L1_p14', card_a: { type: 'text', content: '鱼' }, card_b: { type: 'text', content: '鱼' } },
    { pair_id: 'L1_p15', card_a: { type: 'text', content: '猫' }, card_b: { type: 'text', content: '猫' } },
    { pair_id: 'L1_p16', card_a: { type: 'text', content: '狗' }, card_b: { type: 'text', content: '狗' } },
    { pair_id: 'L1_p17', card_a: { type: 'text', content: '牛' }, card_b: { type: 'text', content: '牛' } },
    { pair_id: 'L1_p18', card_a: { type: 'text', content: '羊' }, card_b: { type: 'text', content: '羊' } },
    { pair_id: 'L1_p19', card_a: { type: 'text', content: '马' }, card_b: { type: 'text', content: '马' } },
    { pair_id: 'L1_p20', card_a: { type: 'text', content: '虎' }, card_b: { type: 'text', content: '虎' } },
    { pair_id: 'L1_p21', card_a: { type: 'text', content: '大' }, card_b: { type: 'text', content: '大' } },
    { pair_id: 'L1_p22', card_a: { type: 'text', content: '小' }, card_b: { type: 'text', content: '小' } },
    { pair_id: 'L1_p23', card_a: { type: 'text', content: '上' }, card_b: { type: 'text', content: '上' } },
    { pair_id: 'L1_p24', card_a: { type: 'text', content: '下' }, card_b: { type: 'text', content: '下' } },
    { pair_id: 'L1_p25', card_a: { type: 'text', content: '红' }, card_b: { type: 'text', content: '红' } },
    { pair_id: 'L1_p26', card_a: { type: 'text', content: '蓝' }, card_b: { type: 'text', content: '蓝' } },
    { pair_id: 'L1_p27', card_a: { type: 'text', content: '绿' }, card_b: { type: 'text', content: '绿' } },
    { pair_id: 'L1_p28', card_a: { type: 'text', content: '黄' }, card_b: { type: 'text', content: '黄' } },
    { pair_id: 'L1_p29', card_a: { type: 'text', content: '天' }, card_b: { type: 'text', content: '天' } },
    { pair_id: 'L1_p30', card_a: { type: 'text', content: '地' }, card_b: { type: 'text', content: '地' } },
  ],
  // L2：近义词配对 —— 30对
  L2: [
    { pair_id: 'L2_p01', card_a: { type: 'text', content: '高兴' }, card_b: { type: 'text', content: '快乐' } },
    { pair_id: 'L2_p02', card_a: { type: 'text', content: '漂亮' }, card_b: { type: 'text', content: '美丽' } },
    { pair_id: 'L2_p03', card_a: { type: 'text', content: '害怕' }, card_b: { type: 'text', content: '恐惧' } },
    { pair_id: 'L2_p04', card_a: { type: 'text', content: '聪明' }, card_b: { type: 'text', content: '智慧' } },
    { pair_id: 'L2_p05', card_a: { type: 'text', content: '勇敢' }, card_b: { type: 'text', content: '胆大' } },
    { pair_id: 'L2_p06', card_a: { type: 'text', content: '悲伤' }, card_b: { type: 'text', content: '难过' } },
    { pair_id: 'L2_p07', card_a: { type: 'text', content: '奔跑' }, card_b: { type: 'text', content: '飞奔' } },
    { pair_id: 'L2_p08', card_a: { type: 'text', content: '帮助' }, card_b: { type: 'text', content: '援助' } },
    { pair_id: 'L2_p09', card_a: { type: 'text', content: '寻找' }, card_b: { type: 'text', content: '寻觅' } },
    { pair_id: 'L2_p10', card_a: { type: 'text', content: '开心' }, card_b: { type: 'text', content: '愉快' } },
    { pair_id: 'L2_p11', card_a: { type: 'text', content: '温柔' }, card_b: { type: 'text', content: '温和' } },
    { pair_id: 'L2_p12', card_a: { type: 'text', content: '坚强' }, card_b: { type: 'text', content: '坚韧' } },
    { pair_id: 'L2_p13', card_a: { type: 'text', content: '思念' }, card_b: { type: 'text', content: '想念' } },
    { pair_id: 'L2_p14', card_a: { type: 'text', content: '宽广' }, card_b: { type: 'text', content: '辽阔' } },
    { pair_id: 'L2_p15', card_a: { type: 'text', content: '清晰' }, card_b: { type: 'text', content: '清楚' } },
    { pair_id: 'L2_p16', card_a: { type: 'text', content: '珍贵' }, card_b: { type: 'text', content: '宝贵' } },
    { pair_id: 'L2_p17', card_a: { type: 'text', content: '迅速' }, card_b: { type: 'text', content: '快速' } },
    { pair_id: 'L2_p18', card_a: { type: 'text', content: '安静' }, card_b: { type: 'text', content: '宁静' } },
    { pair_id: 'L2_p19', card_a: { type: 'text', content: '欢喜' }, card_b: { type: 'text', content: '喜悦' } },
    { pair_id: 'L2_p20', card_a: { type: 'text', content: '忧愁' }, card_b: { type: 'text', content: '忧郁' } },
    { pair_id: 'L2_p21', card_a: { type: 'text', content: '明亮' }, card_b: { type: 'text', content: '光亮' } },
    { pair_id: 'L2_p22', card_a: { type: 'text', content: '柔软' }, card_b: { type: 'text', content: '柔和' } },
    { pair_id: 'L2_p23', card_a: { type: 'text', content: '强壮' }, card_b: { type: 'text', content: '健壮' } },
    { pair_id: 'L2_p24', card_a: { type: 'text', content: '仔细' }, card_b: { type: 'text', content: '认真' } },
    { pair_id: 'L2_p25', card_a: { type: 'text', content: '喜爱' }, card_b: { type: 'text', content: '热爱' } },
    { pair_id: 'L2_p26', card_a: { type: 'text', content: '担心' }, card_b: { type: 'text', content: '忧虑' } },
    { pair_id: 'L2_p27', card_a: { type: 'text', content: '奇怪' }, card_b: { type: 'text', content: '奇特' } },
    { pair_id: 'L2_p28', card_a: { type: 'text', content: '整洁' }, card_b: { type: 'text', content: '干净' } },
    { pair_id: 'L2_p29', card_a: { type: 'text', content: '疲惫' }, card_b: { type: 'text', content: '疲倦' } },
    { pair_id: 'L2_p30', card_a: { type: 'text', content: '聪慧' }, card_b: { type: 'text', content: '机智' } },
  ],
  // L3：反义词配对 —— 30对
  L3: [
    { pair_id: 'L3_p01', card_a: { type: 'text', content: '黑暗' }, card_b: { type: 'text', content: '光明' } },
    { pair_id: 'L3_p02', card_a: { type: 'text', content: '寒冷' }, card_b: { type: 'text', content: '温暖' } },
    { pair_id: 'L3_p03', card_a: { type: 'text', content: '喜欢' }, card_b: { type: 'text', content: '讨厌' } },
    { pair_id: 'L3_p04', card_a: { type: 'text', content: '开始' }, card_b: { type: 'text', content: '结束' } },
    { pair_id: 'L3_p05', card_a: { type: 'text', content: '胜利' }, card_b: { type: 'text', content: '失败' } },
    { pair_id: 'L3_p06', card_a: { type: 'text', content: '诚实' }, card_b: { type: 'text', content: '虚假' } },
    { pair_id: 'L3_p07', card_a: { type: 'text', content: '努力' }, card_b: { type: 'text', content: '懒惰' } },
    { pair_id: 'L3_p08', card_a: { type: 'text', content: '团结' }, card_b: { type: 'text', content: '分裂' } },
    { pair_id: 'L3_p09', card_a: { type: 'text', content: '善良' }, card_b: { type: 'text', content: '凶恶' } },
    { pair_id: 'L3_p10', card_a: { type: 'text', content: '谦虚' }, card_b: { type: 'text', content: '骄傲' } },
    { pair_id: 'L3_p11', card_a: { type: 'text', content: '宽容' }, card_b: { type: 'text', content: '苛刻' } },
    { pair_id: 'L3_p12', card_a: { type: 'text', content: '勤奋' }, card_b: { type: 'text', content: '懈怠' } },
    { pair_id: 'L3_p13', card_a: { type: 'text', content: '慷慨' }, card_b: { type: 'text', content: '吝啬' } },
    { pair_id: 'L3_p14', card_a: { type: 'text', content: '坚定' }, card_b: { type: 'text', content: '动摇' } },
    { pair_id: 'L3_p15', card_a: { type: 'text', content: '乐观' }, card_b: { type: 'text', content: '悲观' } },
    { pair_id: 'L3_p16', card_a: { type: 'text', content: '真诚' }, card_b: { type: 'text', content: '虚伪' } },
    { pair_id: 'L3_p17', card_a: { type: 'text', content: '聪慧' }, card_b: { type: 'text', content: '愚笨' } },
    { pair_id: 'L3_p18', card_a: { type: 'text', content: '勇猛' }, card_b: { type: 'text', content: '懦弱' } },
    { pair_id: 'L3_p19', card_a: { type: 'text', content: '繁荣' }, card_b: { type: 'text', content: '衰败' } },
    { pair_id: 'L3_p20', card_a: { type: 'text', content: '和平' }, card_b: { type: 'text', content: '战争' } },
    { pair_id: 'L3_p21', card_a: { type: 'text', content: '自由' }, card_b: { type: 'text', content: '束缚' } },
    { pair_id: 'L3_p22', card_a: { type: 'text', content: '高尚' }, card_b: { type: 'text', content: '卑鄙' } },
    { pair_id: 'L3_p23', card_a: { type: 'text', content: '坚毅' }, card_b: { type: 'text', content: '软弱' } },
    { pair_id: 'L3_p24', card_a: { type: 'text', content: '博学' }, card_b: { type: 'text', content: '无知' } },
    { pair_id: 'L3_p25', card_a: { type: 'text', content: '公正' }, card_b: { type: 'text', content: '偏颇' } },
    { pair_id: 'L3_p26', card_a: { type: 'text', content: '进步' }, card_b: { type: 'text', content: '退步' } },
    { pair_id: 'L3_p27', card_a: { type: 'text', content: '创新' }, card_b: { type: 'text', content: '守旧' } },
    { pair_id: 'L3_p28', card_a: { type: 'text', content: '清廉' }, card_b: { type: 'text', content: '腐败' } },
    { pair_id: 'L3_p29', card_a: { type: 'text', content: '奉献' }, card_b: { type: 'text', content: '自私' } },
    { pair_id: 'L3_p30', card_a: { type: 'text', content: '包容' }, card_b: { type: 'text', content: '排斥' } },
  ],
}

const PAIRS_PER_SESSION = 10  // 每次从30对中随机抽10对

const PREVIEW_DURATION = { L1: 1500, L2: 1000, L3: 800 }
const GAME_TIMEOUT = 120
const MISMATCH_DELAY = 800
const FLIP_ANIM_DURATION = 300

export default {
  name: 'FlipCardGame',
  components: { FlipCard },
  data() {
    return {
      difficulty: 'L1',
      taskId: null,
      cards: [],
      phase: 'loading',
      flippedCards: [],
      isAnimating: false,
      flipCount: 0,
      matchedPairs: 0,
      timeLeft: GAME_TIMEOUT,
      timerInterval: null,
      startTime: null,
      elapsedSeconds: 0,
      showTimeout: false,
      starsEarned: 0,
      showExitModal: false,
    }
  },
  computed: {
    totalPairs() { return this.cards.length / 2 },
  },
  onLoad(options) {
    this.difficulty = options.difficulty || 'L1'
    this.taskId = options.task_id ? parseInt(options.task_id) : null
    this.initGame()
  },
  onUnload() { this._clearTimer() },
  methods: {
    initGame() {
      this.phase = 'loading'
      this.flipCount = 0
      this.matchedPairs = 0
      this.flippedCards = []
      this.isAnimating = false
      this.showTimeout = false
      this.starsEarned = 0
      this.timeLeft = GAME_TIMEOUT
      this.elapsedSeconds = 0
      this._clearTimer()

      const allPairs = LOCAL_DECKS[this.difficulty] || LOCAL_DECKS.L1
      // 从30对中随机抽取10对
      const shuffledAll = [...allPairs]
      for (let i = shuffledAll.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffledAll[i], shuffledAll[j]] = [shuffledAll[j], shuffledAll[i]]
      }
      const pairs = shuffledAll.slice(0, PAIRS_PER_SESSION)
      const rawCards = []
      let idx = 1
      for (const pair of pairs) {
        rawCards.push({ id: `card_${idx++}`, pairId: pair.pair_id, content: pair.card_a, isFlipped: false, isMatched: false })
        rawCards.push({ id: `card_${idx++}`, pairId: pair.pair_id, content: pair.card_b, isFlipped: false, isMatched: false })
      }
      for (let i = rawCards.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [rawCards[i], rawCards[j]] = [rawCards[j], rawCards[i]]
      }
      this.cards = rawCards
      this._startPreview()
    },
    _startPreview() {
      this.phase = 'preview'
      this.cards = this.cards.map(c => ({ ...c, isFlipped: true }))
      const duration = PREVIEW_DURATION[this.difficulty] || 1500
      setTimeout(() => {
        this.cards = this.cards.map(c => ({ ...c, isFlipped: false }))
        setTimeout(() => {
          this.phase = 'playing'
          this.startTime = Date.now()
          this._startTimer()
        }, FLIP_ANIM_DURATION + 50)
      }, duration)
    },
    _startTimer() {
      this._clearTimer()
      this.timerInterval = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) { this._clearTimer(); this._onTimeout() }
      }, 1000)
    },
    _clearTimer() {
      if (this.timerInterval) { clearInterval(this.timerInterval); this.timerInterval = null }
    },
    _onTimeout() {
      if (this.phase !== 'playing') return
      this.phase = 'timeout'
      this.showTimeout = true
    },
    onCardClick(card) {
      if (this.phase !== 'playing' || card.isFlipped || card.isMatched || this.isAnimating || this.flippedCards.length >= 2) return
      AudioManager.playSFX('flip')
      this._setCardFlipped(card.id, true)
      this.flippedCards = [...this.flippedCards, card]
      if (this.flippedCards.length === 2) { this.flipCount++; this._checkMatch() }
    },
    _checkMatch() {
      const [a, b] = this.flippedCards
      this.isAnimating = true
      if (a.pairId === b.pairId) {
        setTimeout(() => {
          this._setCardMatched(a.id); this._setCardMatched(b.id)
          this.matchedPairs++
          AudioManager.playSFX('correct')
          this.flippedCards = []
          this.isAnimating = false
          if (this.matchedPairs >= this.totalPairs) this._finishGame()
        }, FLIP_ANIM_DURATION)
      } else {
        setTimeout(() => {
          AudioManager.playSFX('wrong')
          this._setCardFlipped(a.id, false); this._setCardFlipped(b.id, false)
          this.flippedCards = []
          setTimeout(() => { this.isAnimating = false }, FLIP_ANIM_DURATION)
        }, MISMATCH_DELAY)
      }
    },
    _setCardFlipped(id, flipped) { this.cards = this.cards.map(c => c.id === id ? { ...c, isFlipped: flipped } : c) },
    _setCardMatched(id) { this.cards = this.cards.map(c => c.id === id ? { ...c, isFlipped: true, isMatched: true } : c) },
    async _finishGame() {
      this._clearTimer()
      this.elapsedSeconds = Math.round((Date.now() - this.startTime) / 1000)
      this.starsEarned = calcFlipCardStars(this.flipCount, this.totalPairs)
      AudioManager.playSFX('complete')
      this.phase = 'result'
      await this._submitResult()
    },
    async _submitResult() {
      const accuracy = this.totalPairs > 0
        ? Math.round((this.matchedPairs / this.totalPairs) * 100)
        : 0
      const payload = buildFlipCardPayload({
        taskId: this.taskId, difficulty: this.difficulty, starsEarned: this.starsEarned,
        durationSeconds: this.elapsedSeconds, totalPairs: this.totalPairs,
        flipCount: this.flipCount, matchCount: this.matchedPairs,
      })
      if (this.taskId) {
        try { await completeTask(this.taskId, payload) } catch (e) { enqueueRecord({ taskId: this.taskId, payload }) }
      } else {
        // 从挑战tab直接进入，没有task_id，自动创建并完成任务以记录星星
        try {
          const child = getCurrentChild()
          if (child?.id) {
            const task = await createTask({
              child_id: child.id,
              task_type: 'flip_card',
              task_name: '翻牌记忆挑战',
              scheduled_date: new Date().toISOString().split('T')[0],
            })
            await completeTask(task.id, { ...payload, task_id: task.id })
          }
        } catch (e) { console.warn('自动创建任务失败', e) }
      }
      // 保存结果供结算页使用（与前6种游戏格式对齐）
      uni.setStorageSync('last_training_result', {
        game_type: 'flip_card',
        correct_count: this.matchedPairs,
        total_count: this.totalPairs,
        accuracy,
        stars: this.starsEarned,
        mode: 'training',
      })
      // 跳转到统一结算页
      uni.redirectTo({ url: '/pages/child/training-reward/index' })
    },
    restartGame() { this.showTimeout = false; this.initGame() },
    finishGame() { uni.navigateBack({ delta: 1 }) },
    goBack() { this._clearTimer(); uni.navigateBack({ delta: 1 }) },
    exitGame() {
      this.showExitModal = true
    },
    doExit() {
      this._clearTimer()
      this.showExitModal = false
      uni.navigateBack({ delta: 1 })
    },
  },
}
</script>

<style scoped>
.page-container { min-height: 100vh; background: linear-gradient(160deg, #FFFBEB 0%, #FEF3C7 100%); display: flex; flex-direction: column; width: 100%; box-sizing: border-box; }
.top-bar { display: flex; flex-direction: row; align-items: center; justify-content: space-between; padding: 56rpx 32rpx 20rpx; background: rgba(255,255,255,0.92); box-shadow: 0 2rpx 12rpx rgba(251,191,36,0.12); flex-shrink: 0; }
.back-btn { width: 72rpx; height: 72rpx; border-radius: 50%; background: #FEF3C7; display: flex; align-items: center; justify-content: center; border: 2rpx solid #FDE68A; }
.back-btn:active { transform: scale(0.92); }
.back-btn .ph { font-size: 32rpx; color: #D97706; }
.title-area { flex: 1; display: flex; align-items: center; justify-content: center; text-align: center; }
.game-title { font-size: 32rpx; font-weight: 800; color: #92400E; }
.top-stats { display: flex; flex-direction: row; gap: 12rpx; }
.stat-chip { display: flex; flex-direction: row; align-items: center; gap: 6rpx; background: #FEF3C7; padding: 10rpx 18rpx; border-radius: 24rpx; border: 2rpx solid #FDE68A; }
.stat-chip .ph { font-size: 26rpx; color: #D97706; }
.stat-val { font-size: 26rpx; font-weight: 800; color: #92400E; }
.timer-chip.warning { background: #FEF2F2; border-color: #FECACA; }
.timer-chip.warning .ph, .timer-chip.warning .stat-val { color: #EF4444; }
.content-area { flex: 1; padding: 24rpx 20rpx 0; width: 100%; box-sizing: border-box; }
.card-grid { display: grid; gap: 16rpx; margin-bottom: 28rpx; }
.grid-4col { grid-template-columns: repeat(4, 1fr); }
.progress-bar-area { margin: 0 4rpx 16rpx; }
.progress-label { display: flex; flex-direction: row; align-items: center; gap: 8rpx; font-size: 26rpx; font-weight: 700; color: #92400E; margin-bottom: 10rpx; }
.progress-label .ph { font-size: 28rpx; color: #D97706; }
.progress-track { height: 12rpx; background: #FDE68A; border-radius: 6rpx; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #FCD34D, #F59E0B); border-radius: 6rpx; transition: width 0.4s ease; }
.overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center; animation: fadeIn 0.2s; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.modal-card { background: #FFFFFF; width: 88%; max-width: 620rpx; border-radius: 40rpx; padding: 52rpx 40rpx 40rpx; display: flex; flex-direction: column; align-items: center; gap: 20rpx; animation: popIn 0.3s cubic-bezier(0.34,1.56,0.64,1); }
@keyframes popIn { from { opacity: 0; transform: scale(0.8); } to { opacity: 1; transform: scale(1); } }
.timeout-card { border-top: 8rpx solid #F59E0B; }
.result-card { border-top: 8rpx solid #7C3AED; }
.modal-emoji { font-size: 88rpx; line-height: 1; }
.modal-title { font-size: 44rpx; font-weight: 900; color: #2D3748; }
.modal-desc { font-size: 28rpx; color: #718096; font-weight: 500; text-align: center; }
.modal-btn { width: 100%; border-radius: 24rpx; padding: 28rpx; font-size: 30rpx; font-weight: 700; display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 8rpx; }
.modal-btn:active { transform: scale(0.97); }
.btn-retry { background: linear-gradient(135deg, #FCD34D, #F59E0B); color: #FFFFFF; box-shadow: 0 4rpx 16rpx rgba(245,158,11,0.35); }
.btn-back { background: #F3F4F6; color: #6B7280; margin-top: -8rpx; }
.btn-finish { background: linear-gradient(135deg, #FCD34D, #F59E0B); color: #FFFFFF; box-shadow: 0 4rpx 16rpx rgba(245,158,11,0.35); }
.btn-finish .ph { font-size: 30rpx; }
.btn-retry-sm { background: #FEF3C7; color: #D97706; margin-top: -8rpx; }
.result-emoji { font-size: 96rpx; line-height: 1; }
.result-title { font-size: 44rpx; font-weight: 900; color: #92400E; }
.result-stars { display: flex; flex-direction: row; gap: 8rpx; }
.result-star { font-size: 48rpx; opacity: 0.2; transition: all 0.3s; }
.result-star.earned { opacity: 1; animation: starPop 0.4s cubic-bezier(0.34,1.56,0.64,1); }
@keyframes starPop { from { transform: scale(0); } to { transform: scale(1); } }
.result-stats { display: flex; flex-direction: row; align-items: center; background: #FFFBEB; border-radius: 20rpx; padding: 20rpx 32rpx; width: 100%; }
.stat-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4rpx; }
.stat-num { font-size: 44rpx; font-weight: 900; color: #D97706; }
.stat-label { font-size: 22rpx; color: #B45309; font-weight: 600; }
.exit-btn { width: 64rpx; height: 64rpx; border-radius: 50%; background: rgba(255,107,107,0.1); border: 2rpx solid rgba(255,107,107,0.2); display: flex; align-items: center; justify-content: center; }
.exit-btn .ph { font-size: 28rpx; color: #FF6B6B; }

/* 退出确认弹窗 */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 9999;
  display: flex; justify-content: center; align-items: center;
}
.modal-content {
  background: #FFFFFF;
  width: 85%; max-width: 640rpx;
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.15);
}
.modal-icon {
  width: 112rpx; height: 112rpx;
  border-radius: 28rpx;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 28rpx;
}
.modal-icon.warning { background: linear-gradient(135deg, #FFF9C4, #FFE082); }
.modal-icon.warning .ph { font-size: 56rpx; color: #F57F17; }
.modal-title { font-size: 36rpx; font-weight: 800; color: #2D3748; margin-bottom: 12rpx; }
.modal-desc { font-size: 26rpx; color: #718096; text-align: center; line-height: 1.6; margin-bottom: 36rpx; font-weight: 500; }
.modal-btn { width: 100%; border-radius: 16rpx; padding: 28rpx; font-size: 28rpx; font-weight: 700; margin-bottom: 16rpx; transition: all 0.2s; }
.modal-btn.outline { background: #F5F5F5; color: #718096; }
.modal-btn.primary { background: linear-gradient(135deg, #4F9EF8, #3B82F6); color: #FFFFFF; box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.25); }
</style>
