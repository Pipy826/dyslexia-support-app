<template>
  <view
    class="page-container"
    @touchmove.stop.prevent="onPageTouchMove"
    @touchend.stop="onPageTouchEnd"
    @touchcancel.stop="onPageTouchEnd"
  >

    <!-- 顶部栏 -->
    <view class="top-bar">
      <view class="title-area">
        <text class="game-title">连一连</text>
        <text class="game-instruction" v-if="currentQuestion">{{ currentQuestion.instruction }}</text>
      </view>
      <view class="top-right-area">
        <view class="timer-chip" :class="{ warning: timeLeft <= 20 }">
          <text class="ph ph-timer"></text>
          <text class="timer-val">{{ timeLeft }}s</text>
        </view>
        <view class="exit-btn" @click="exitGame">
          <text class="ph ph-x"></text>
        </view>
      </view>
    </view>

    <!-- 游戏区域 -->
    <view class="game-area" v-if="phase === 'playing' || phase === 'result'">

      <!-- 三列布局：左侧项 | 连线层 | 右侧项 -->
      <view class="columns-wrapper" id="columns-wrapper">

        <!-- 左侧项列表 -->
        <view class="items-col items-left">
          <view
            v-for="item in leftItems"
            :key="item.id"
            :id="'left_' + item.id"
            :class="['item-card', 'item-left', {
              'item-connected': isLeftConnected(item.id),
              'item-correct': isLeftCorrect(item.id),
              'item-wrong': isLeftWrong(item.id),
              'item-dragging': draggingLeftId === item.id,
            }]"
            @touchstart.stop.prevent="onTouchStart($event, item)"
          >
            <text v-if="item.type === 'emoji'" class="item-emoji">{{ item.content }}</text>
            <text v-else class="item-text">{{ item.content }}</text>
          </view>
        </view>

        <!-- 连线层（绝对定位覆盖在中间） -->
        <view class="line-layer-wrapper" id="line-layer-wrapper">
          <connect-line
            :connections="connections"
            :left-positions="leftPositions"
            :right-positions="rightPositions"
            :temp-line="tempLine"
            :width="lineLayerWidth"
            :height="lineLayerHeight"
            @line-click="onLineClick"
          ></connect-line>
        </view>

        <!-- 右侧项列表 -->
        <view class="items-col items-right">
          <view
            v-for="item in rightItems"
            :key="item.id"
            :id="'right_' + item.id"
            :class="['item-card', 'item-right', {
              'item-connected': isRightConnected(item.id),
              'item-correct': isRightCorrect(item.id),
              'item-wrong': isRightWrong(item.id),
            }]"
          >
            <text v-if="item.type === 'emoji'" class="item-emoji">{{ item.content }}</text>
            <text v-else class="item-text">{{ item.content }}</text>
          </view>
        </view>

      </view>

      <!-- 底部进度提示 + 提交按钮 -->
      <view class="bottom-bar">
        <view class="progress-info">
          <text class="ph ph-link"></text>
          <text class="progress-text">已连 {{ correctCount }} / {{ totalPairs }} 对</text>
        </view>
        <button
          class="submit-btn"
          :disabled="correctCount < totalPairs"
          @click="onSubmitClick"
        >
          <text class="ph ph-check-circle"></text>
          完成
        </button>
      </view>

    </view>

    <!-- 加载中 -->
    <view class="loading-area" v-if="phase === 'loading'">
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 退出确认弹窗 -->
    <view class="exit-modal-overlay" v-if="showExitModal" @click="showExitModal = false">
      <view class="exit-modal-content" @click.stop>
        <view class="exit-modal-icon">
          <text class="ph ph-warning"></text>
        </view>
        <view class="exit-modal-title">要休息一下吗？</view>
        <view class="exit-modal-desc">当前进度不会保存哦，下次重新开始。</view>
        <button class="exit-modal-btn outline" @click="doExit">退出游戏</button>
        <button class="exit-modal-btn primary" @click="showExitModal = false">继续游戏</button>
      </view>
    </view>

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

    <!-- 结果弹窗 -->
    <view class="overlay" v-if="phase === 'result'">
      <view class="modal-card result-card">
        <view class="result-emoji">{{ starsEarned >= 3 ? '🏆' : starsEarned >= 2 ? '😊' : starsEarned >= 1 ? '🌟' : '💪' }}</view>
        <view class="result-title">{{ starsEarned > 0 ? '太棒了！' : '继续加油！' }}</view>
        <view class="result-stars">
          <text v-for="i in 3" :key="i" :class="['result-star', { earned: i <= starsEarned }]">⭐</text>
        </view>
        <view class="result-stats">
          <view class="stat-item">
            <view class="stat-num">{{ correctCount }}</view>
            <view class="stat-label">正确对数</view>
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
import ConnectLine from '../../../components/game/ConnectLine.vue'
import AudioManager from '../../../utils/audio.js'
import { calcConnectGameStars, removeConnection } from '../../../utils/gameScoring.js'
import { buildConnectGamePayload, enqueueRecord } from '../../../utils/gameDataBuilder.js'
import { completeTask, createTask } from '../../../api/training.js'
import { getCurrentChild } from '../../../utils/auth.js'

// ─── 本地题目数据（每个难度30题，每次随机抽1题展示）────────────────────────

const LOCAL_QUESTIONS = {
  // L1：相同汉字连线（认字练习）—— 30题
  L1: [
    { id: 'cg_L1_001', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '山' }, right: { type: 'text', content: '山' } }, { left: { type: 'text', content: '水' }, right: { type: 'text', content: '水' } }, { left: { type: 'text', content: '日' }, right: { type: 'text', content: '日' } }, { left: { type: 'text', content: '月' }, right: { type: 'text', content: '月' } }], time_limit: 60 },
    { id: 'cg_L1_002', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '火' }, right: { type: 'text', content: '火' } }, { left: { type: 'text', content: '木' }, right: { type: 'text', content: '木' } }, { left: { type: 'text', content: '土' }, right: { type: 'text', content: '土' } }, { left: { type: 'text', content: '金' }, right: { type: 'text', content: '金' } }], time_limit: 60 },
    { id: 'cg_L1_003', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '风' }, right: { type: 'text', content: '风' } }, { left: { type: 'text', content: '云' }, right: { type: 'text', content: '云' } }, { left: { type: 'text', content: '花' }, right: { type: 'text', content: '花' } }, { left: { type: 'text', content: '草' }, right: { type: 'text', content: '草' } }], time_limit: 60 },
    { id: 'cg_L1_004', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '鸟' }, right: { type: 'text', content: '鸟' } }, { left: { type: 'text', content: '鱼' }, right: { type: 'text', content: '鱼' } }, { left: { type: 'text', content: '猫' }, right: { type: 'text', content: '猫' } }, { left: { type: 'text', content: '狗' }, right: { type: 'text', content: '狗' } }], time_limit: 60 },
    { id: 'cg_L1_005', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '牛' }, right: { type: 'text', content: '牛' } }, { left: { type: 'text', content: '羊' }, right: { type: 'text', content: '羊' } }, { left: { type: 'text', content: '马' }, right: { type: 'text', content: '马' } }, { left: { type: 'text', content: '虎' }, right: { type: 'text', content: '虎' } }], time_limit: 60 },
    { id: 'cg_L1_006', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '大' }, right: { type: 'text', content: '大' } }, { left: { type: 'text', content: '小' }, right: { type: 'text', content: '小' } }, { left: { type: 'text', content: '上' }, right: { type: 'text', content: '上' } }, { left: { type: 'text', content: '下' }, right: { type: 'text', content: '下' } }], time_limit: 60 },
    { id: 'cg_L1_007', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '左' }, right: { type: 'text', content: '左' } }, { left: { type: 'text', content: '右' }, right: { type: 'text', content: '右' } }, { left: { type: 'text', content: '前' }, right: { type: 'text', content: '前' } }, { left: { type: 'text', content: '后' }, right: { type: 'text', content: '后' } }], time_limit: 60 },
    { id: 'cg_L1_008', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '红' }, right: { type: 'text', content: '红' } }, { left: { type: 'text', content: '蓝' }, right: { type: 'text', content: '蓝' } }, { left: { type: 'text', content: '绿' }, right: { type: 'text', content: '绿' } }, { left: { type: 'text', content: '黄' }, right: { type: 'text', content: '黄' } }], time_limit: 60 },
    { id: 'cg_L1_009', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '一' }, right: { type: 'text', content: '一' } }, { left: { type: 'text', content: '二' }, right: { type: 'text', content: '二' } }, { left: { type: 'text', content: '三' }, right: { type: 'text', content: '三' } }, { left: { type: 'text', content: '四' }, right: { type: 'text', content: '四' } }], time_limit: 60 },
    { id: 'cg_L1_010', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '五' }, right: { type: 'text', content: '五' } }, { left: { type: 'text', content: '六' }, right: { type: 'text', content: '六' } }, { left: { type: 'text', content: '七' }, right: { type: 'text', content: '七' } }, { left: { type: 'text', content: '八' }, right: { type: 'text', content: '八' } }], time_limit: 60 },
    { id: 'cg_L1_011', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '人' }, right: { type: 'text', content: '人' } }, { left: { type: 'text', content: '口' }, right: { type: 'text', content: '口' } }, { left: { type: 'text', content: '手' }, right: { type: 'text', content: '手' } }, { left: { type: 'text', content: '足' }, right: { type: 'text', content: '足' } }], time_limit: 60 },
    { id: 'cg_L1_012', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '目' }, right: { type: 'text', content: '目' } }, { left: { type: 'text', content: '耳' }, right: { type: 'text', content: '耳' } }, { left: { type: 'text', content: '鼻' }, right: { type: 'text', content: '鼻' } }, { left: { type: 'text', content: '心' }, right: { type: 'text', content: '心' } }], time_limit: 60 },
    { id: 'cg_L1_013', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '天' }, right: { type: 'text', content: '天' } }, { left: { type: 'text', content: '地' }, right: { type: 'text', content: '地' } }, { left: { type: 'text', content: '家' }, right: { type: 'text', content: '家' } }, { left: { type: 'text', content: '国' }, right: { type: 'text', content: '国' } }], time_limit: 60 },
    { id: 'cg_L1_014', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '书' }, right: { type: 'text', content: '书' } }, { left: { type: 'text', content: '笔' }, right: { type: 'text', content: '笔' } }, { left: { type: 'text', content: '纸' }, right: { type: 'text', content: '纸' } }, { left: { type: 'text', content: '字' }, right: { type: 'text', content: '字' } }], time_limit: 60 },
    { id: 'cg_L1_015', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '春' }, right: { type: 'text', content: '春' } }, { left: { type: 'text', content: '夏' }, right: { type: 'text', content: '夏' } }, { left: { type: 'text', content: '秋' }, right: { type: 'text', content: '秋' } }, { left: { type: 'text', content: '冬' }, right: { type: 'text', content: '冬' } }], time_limit: 60 },
    { id: 'cg_L1_016', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '东' }, right: { type: 'text', content: '东' } }, { left: { type: 'text', content: '西' }, right: { type: 'text', content: '西' } }, { left: { type: 'text', content: '南' }, right: { type: 'text', content: '南' } }, { left: { type: 'text', content: '北' }, right: { type: 'text', content: '北' } }], time_limit: 60 },
    { id: 'cg_L1_017', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '爸' }, right: { type: 'text', content: '爸' } }, { left: { type: 'text', content: '妈' }, right: { type: 'text', content: '妈' } }, { left: { type: 'text', content: '哥' }, right: { type: 'text', content: '哥' } }, { left: { type: 'text', content: '姐' }, right: { type: 'text', content: '姐' } }], time_limit: 60 },
    { id: 'cg_L1_018', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '吃' }, right: { type: 'text', content: '吃' } }, { left: { type: 'text', content: '喝' }, right: { type: 'text', content: '喝' } }, { left: { type: 'text', content: '跑' }, right: { type: 'text', content: '跑' } }, { left: { type: 'text', content: '跳' }, right: { type: 'text', content: '跳' } }], time_limit: 60 },
    { id: 'cg_L1_019', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '看' }, right: { type: 'text', content: '看' } }, { left: { type: 'text', content: '听' }, right: { type: 'text', content: '听' } }, { left: { type: 'text', content: '说' }, right: { type: 'text', content: '说' } }, { left: { type: 'text', content: '写' }, right: { type: 'text', content: '写' } }], time_limit: 60 },
    { id: 'cg_L1_020', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '好' }, right: { type: 'text', content: '好' } }, { left: { type: 'text', content: '坏' }, right: { type: 'text', content: '坏' } }, { left: { type: 'text', content: '多' }, right: { type: 'text', content: '多' } }, { left: { type: 'text', content: '少' }, right: { type: 'text', content: '少' } }], time_limit: 60 },
    { id: 'cg_L1_021', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '长' }, right: { type: 'text', content: '长' } }, { left: { type: 'text', content: '短' }, right: { type: 'text', content: '短' } }, { left: { type: 'text', content: '高' }, right: { type: 'text', content: '高' } }, { left: { type: 'text', content: '低' }, right: { type: 'text', content: '低' } }], time_limit: 60 },
    { id: 'cg_L1_022', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '快' }, right: { type: 'text', content: '快' } }, { left: { type: 'text', content: '慢' }, right: { type: 'text', content: '慢' } }, { left: { type: 'text', content: '冷' }, right: { type: 'text', content: '冷' } }, { left: { type: 'text', content: '热' }, right: { type: 'text', content: '热' } }], time_limit: 60 },
    { id: 'cg_L1_023', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '新' }, right: { type: 'text', content: '新' } }, { left: { type: 'text', content: '旧' }, right: { type: 'text', content: '旧' } }, { left: { type: 'text', content: '早' }, right: { type: 'text', content: '早' } }, { left: { type: 'text', content: '晚' }, right: { type: 'text', content: '晚' } }], time_limit: 60 },
    { id: 'cg_L1_024', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '来' }, right: { type: 'text', content: '来' } }, { left: { type: 'text', content: '去' }, right: { type: 'text', content: '去' } }, { left: { type: 'text', content: '开' }, right: { type: 'text', content: '开' } }, { left: { type: 'text', content: '关' }, right: { type: 'text', content: '关' } }], time_limit: 60 },
    { id: 'cg_L1_025', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '哭' }, right: { type: 'text', content: '哭' } }, { left: { type: 'text', content: '笑' }, right: { type: 'text', content: '笑' } }, { left: { type: 'text', content: '爱' }, right: { type: 'text', content: '爱' } }, { left: { type: 'text', content: '恨' }, right: { type: 'text', content: '恨' } }], time_limit: 60 },
    { id: 'cg_L1_026', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '学' }, right: { type: 'text', content: '学' } }, { left: { type: 'text', content: '校' }, right: { type: 'text', content: '校' } }, { left: { type: 'text', content: '老' }, right: { type: 'text', content: '老' } }, { left: { type: 'text', content: '师' }, right: { type: 'text', content: '师' } }], time_limit: 60 },
    { id: 'cg_L1_027', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '苹' }, right: { type: 'text', content: '苹' } }, { left: { type: 'text', content: '果' }, right: { type: 'text', content: '果' } }, { left: { type: 'text', content: '梨' }, right: { type: 'text', content: '梨' } }, { left: { type: 'text', content: '桃' }, right: { type: 'text', content: '桃' } }], time_limit: 60 },
    { id: 'cg_L1_028', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '买' }, right: { type: 'text', content: '买' } }, { left: { type: 'text', content: '卖' }, right: { type: 'text', content: '卖' } }, { left: { type: 'text', content: '问' }, right: { type: 'text', content: '问' } }, { left: { type: 'text', content: '答' }, right: { type: 'text', content: '答' } }], time_limit: 60 },
    { id: 'cg_L1_029', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '弟' }, right: { type: 'text', content: '弟' } }, { left: { type: 'text', content: '妹' }, right: { type: 'text', content: '妹' } }, { left: { type: 'text', content: '爷' }, right: { type: 'text', content: '爷' } }, { left: { type: 'text', content: '奶' }, right: { type: 'text', content: '奶' } }], time_limit: 60 },
    { id: 'cg_L1_030', type: 'text_text', instruction: '把相同的字连起来', pairs: [{ left: { type: 'text', content: '九' }, right: { type: 'text', content: '九' } }, { left: { type: 'text', content: '十' }, right: { type: 'text', content: '十' } }, { left: { type: 'text', content: '百' }, right: { type: 'text', content: '百' } }, { left: { type: 'text', content: '千' }, right: { type: 'text', content: '千' } }], time_limit: 60 },
  ],
  // L2：近义词连线 —— 30题
  L2: [
    { id: 'cg_L2_001', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '高兴' }, right: { type: 'text', content: '快乐' } }, { left: { type: 'text', content: '漂亮' }, right: { type: 'text', content: '美丽' } }, { left: { type: 'text', content: '害怕' }, right: { type: 'text', content: '恐惧' } }, { left: { type: 'text', content: '聪明' }, right: { type: 'text', content: '智慧' } }], time_limit: 75 },
    { id: 'cg_L2_002', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '勇敢' }, right: { type: 'text', content: '胆大' } }, { left: { type: 'text', content: '悲伤' }, right: { type: 'text', content: '难过' } }, { left: { type: 'text', content: '奔跑' }, right: { type: 'text', content: '飞奔' } }, { left: { type: 'text', content: '帮助' }, right: { type: 'text', content: '援助' } }], time_limit: 75 },
    { id: 'cg_L2_003', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '开心' }, right: { type: 'text', content: '愉快' } }, { left: { type: 'text', content: '温柔' }, right: { type: 'text', content: '温和' } }, { left: { type: 'text', content: '坚强' }, right: { type: 'text', content: '坚韧' } }, { left: { type: 'text', content: '思念' }, right: { type: 'text', content: '想念' } }], time_limit: 75 },
    { id: 'cg_L2_004', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '宽广' }, right: { type: 'text', content: '辽阔' } }, { left: { type: 'text', content: '清晰' }, right: { type: 'text', content: '清楚' } }, { left: { type: 'text', content: '珍贵' }, right: { type: 'text', content: '宝贵' } }, { left: { type: 'text', content: '迅速' }, right: { type: 'text', content: '快速' } }], time_limit: 75 },
    { id: 'cg_L2_005', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '安静' }, right: { type: 'text', content: '宁静' } }, { left: { type: 'text', content: '欢喜' }, right: { type: 'text', content: '喜悦' } }, { left: { type: 'text', content: '明亮' }, right: { type: 'text', content: '光亮' } }, { left: { type: 'text', content: '柔软' }, right: { type: 'text', content: '柔和' } }], time_limit: 75 },
    { id: 'cg_L2_006', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '强壮' }, right: { type: 'text', content: '健壮' } }, { left: { type: 'text', content: '仔细' }, right: { type: 'text', content: '认真' } }, { left: { type: 'text', content: '喜爱' }, right: { type: 'text', content: '热爱' } }, { left: { type: 'text', content: '担心' }, right: { type: 'text', content: '忧虑' } }], time_limit: 75 },
    { id: 'cg_L2_007', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '奇怪' }, right: { type: 'text', content: '奇特' } }, { left: { type: 'text', content: '整洁' }, right: { type: 'text', content: '干净' } }, { left: { type: 'text', content: '疲惫' }, right: { type: 'text', content: '疲倦' } }, { left: { type: 'text', content: '聪慧' }, right: { type: 'text', content: '机智' } }], time_limit: 75 },
    { id: 'cg_L2_008', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '忧愁' }, right: { type: 'text', content: '忧郁' } }, { left: { type: 'text', content: '保护' }, right: { type: 'text', content: '守护' } }, { left: { type: 'text', content: '美好' }, right: { type: 'text', content: '美妙' } }, { left: { type: 'text', content: '快活' }, right: { type: 'text', content: '欢乐' } }], time_limit: 75 },
    { id: 'cg_L2_009', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '勤劳' }, right: { type: 'text', content: '勤奋' } }, { left: { type: 'text', content: '善意' }, right: { type: 'text', content: '好意' } }, { left: { type: 'text', content: '感谢' }, right: { type: 'text', content: '感激' } }, { left: { type: 'text', content: '期待' }, right: { type: 'text', content: '盼望' } }], time_limit: 75 },
    { id: 'cg_L2_010', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '惊讶' }, right: { type: 'text', content: '惊奇' } }, { left: { type: 'text', content: '平静' }, right: { type: 'text', content: '平和' } }, { left: { type: 'text', content: '广阔' }, right: { type: 'text', content: '宽阔' } }, { left: { type: 'text', content: '鲜艳' }, right: { type: 'text', content: '艳丽' } }], time_limit: 75 },
    { id: 'cg_L2_011', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '著名' }, right: { type: 'text', content: '有名' } }, { left: { type: 'text', content: '普通' }, right: { type: 'text', content: '平常' } }, { left: { type: 'text', content: '特别' }, right: { type: 'text', content: '特殊' } }, { left: { type: 'text', content: '重要' }, right: { type: 'text', content: '重大' } }], time_limit: 75 },
    { id: 'cg_L2_012', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '完整' }, right: { type: 'text', content: '完全' } }, { left: { type: 'text', content: '正确' }, right: { type: 'text', content: '准确' } }, { left: { type: 'text', content: '困难' }, right: { type: 'text', content: '艰难' } }, { left: { type: 'text', content: '容易' }, right: { type: 'text', content: '简单' } }], time_limit: 75 },
    { id: 'cg_L2_013', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '努力' }, right: { type: 'text', content: '用功' } }, { left: { type: 'text', content: '认真' }, right: { type: 'text', content: '专心' } }, { left: { type: 'text', content: '进步' }, right: { type: 'text', content: '提高' } }, { left: { type: 'text', content: '友好' }, right: { type: 'text', content: '友善' } }], time_limit: 75 },
    { id: 'cg_L2_014', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '热情' }, right: { type: 'text', content: '热心' } }, { left: { type: 'text', content: '亲切' }, right: { type: 'text', content: '亲近' } }, { left: { type: 'text', content: '满足' }, right: { type: 'text', content: '满意' } }, { left: { type: 'text', content: '失望' }, right: { type: 'text', content: '沮丧' } }], time_limit: 75 },
    { id: 'cg_L2_015', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '希望' }, right: { type: 'text', content: '愿望' } }, { left: { type: 'text', content: '梦想' }, right: { type: 'text', content: '理想' } }, { left: { type: 'text', content: '信心' }, right: { type: 'text', content: '信念' } }, { left: { type: 'text', content: '勇气' }, right: { type: 'text', content: '胆量' } }], time_limit: 75 },
    { id: 'cg_L2_016', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '创造' }, right: { type: 'text', content: '创作' } }, { left: { type: 'text', content: '发现' }, right: { type: 'text', content: '发觉' } }, { left: { type: 'text', content: '探索' }, right: { type: 'text', content: '探究' } }, { left: { type: 'text', content: '研究' }, right: { type: 'text', content: '探讨' } }], time_limit: 75 },
    { id: 'cg_L2_017', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '珍惜' }, right: { type: 'text', content: '爱惜' } }, { left: { type: 'text', content: '节约' }, right: { type: 'text', content: '节省' } }, { left: { type: 'text', content: '有趣' }, right: { type: 'text', content: '有意思' } }, { left: { type: 'text', content: '无聊' }, right: { type: 'text', content: '枯燥' } }], time_limit: 75 },
    { id: 'cg_L2_018', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '安全' }, right: { type: 'text', content: '平安' } }, { left: { type: 'text', content: '健康' }, right: { type: 'text', content: '强健' } }, { left: { type: 'text', content: '开始' }, right: { type: 'text', content: '起始' } }, { left: { type: 'text', content: '结束' }, right: { type: 'text', content: '完成' } }], time_limit: 75 },
    { id: 'cg_L2_019', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '增加' }, right: { type: 'text', content: '增多' } }, { left: { type: 'text', content: '减少' }, right: { type: 'text', content: '减小' } }, { left: { type: 'text', content: '扩大' }, right: { type: 'text', content: '扩展' } }, { left: { type: 'text', content: '缩小' }, right: { type: 'text', content: '缩减' } }], time_limit: 75 },
    { id: 'cg_L2_020', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '提问' }, right: { type: 'text', content: '询问' } }, { left: { type: 'text', content: '回答' }, right: { type: 'text', content: '解答' } }, { left: { type: 'text', content: '讨论' }, right: { type: 'text', content: '商讨' } }, { left: { type: 'text', content: '分享' }, right: { type: 'text', content: '共享' } }], time_limit: 75 },
    { id: 'cg_L2_021', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '观察' }, right: { type: 'text', content: '观看' } }, { left: { type: 'text', content: '思考' }, right: { type: 'text', content: '思索' } }, { left: { type: 'text', content: '记忆' }, right: { type: 'text', content: '记住' } }, { left: { type: 'text', content: '理解' }, right: { type: 'text', content: '明白' } }], time_limit: 75 },
    { id: 'cg_L2_022', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '表达' }, right: { type: 'text', content: '表述' } }, { left: { type: 'text', content: '描述' }, right: { type: 'text', content: '描写' } }, { left: { type: 'text', content: '解释' }, right: { type: 'text', content: '说明' } }, { left: { type: 'text', content: '介绍' }, right: { type: 'text', content: '推介' } }], time_limit: 75 },
    { id: 'cg_L2_023', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '合作' }, right: { type: 'text', content: '协作' } }, { left: { type: 'text', content: '支持' }, right: { type: 'text', content: '支援' } }, { left: { type: 'text', content: '温暖' }, right: { type: 'text', content: '暖和' } }, { left: { type: 'text', content: '清凉' }, right: { type: 'text', content: '凉爽' } }], time_limit: 75 },
    { id: 'cg_L2_024', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '高大' }, right: { type: 'text', content: '高耸' } }, { left: { type: 'text', content: '微小' }, right: { type: 'text', content: '细小' } }, { left: { type: 'text', content: '宽敞' }, right: { type: 'text', content: '宽阔' } }, { left: { type: 'text', content: '狭窄' }, right: { type: 'text', content: '狭小' } }], time_limit: 75 },
    { id: 'cg_L2_025', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '丰富' }, right: { type: 'text', content: '充足' } }, { left: { type: 'text', content: '整齐' }, right: { type: 'text', content: '有序' } }, { left: { type: 'text', content: '混乱' }, right: { type: 'text', content: '杂乱' } }, { left: { type: 'text', content: '危险' }, right: { type: 'text', content: '危急' } }], time_limit: 75 },
    { id: 'cg_L2_026', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '继续' }, right: { type: 'text', content: '持续' } }, { left: { type: 'text', content: '停止' }, right: { type: 'text', content: '停下' } }, { left: { type: 'text', content: '坚持' }, right: { type: 'text', content: '坚守' } }, { left: { type: 'text', content: '放弃' }, right: { type: 'text', content: '舍弃' } }], time_limit: 75 },
    { id: 'cg_L2_027', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '快乐' }, right: { type: 'text', content: '幸福' } }, { left: { type: 'text', content: '痛苦' }, right: { type: 'text', content: '苦恼' } }, { left: { type: 'text', content: '智慧' }, right: { type: 'text', content: '才智' } }, { left: { type: 'text', content: '品德' }, right: { type: 'text', content: '品质' } }], time_limit: 75 },
    { id: 'cg_L2_028', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '力量' }, right: { type: 'text', content: '力气' } }, { left: { type: 'text', content: '目标' }, right: { type: 'text', content: '志向' } }, { left: { type: 'text', content: '古老' }, right: { type: 'text', content: '陈旧' } }, { left: { type: 'text', content: '新颖' }, right: { type: 'text', content: '新奇' } }], time_limit: 75 },
    { id: 'cg_L2_029', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '精确' }, right: { type: 'text', content: '准确' } }, { left: { type: 'text', content: '严格' }, right: { type: 'text', content: '严厉' } }, { left: { type: 'text', content: '细致' }, right: { type: 'text', content: '仔细' } }, { left: { type: 'text', content: '粗糙' }, right: { type: 'text', content: '粗劣' } }], time_limit: 75 },
    { id: 'cg_L2_030', type: 'text_text', instruction: '把意思相近的词语连起来', pairs: [{ left: { type: 'text', content: '自信' }, right: { type: 'text', content: '自豪' } }, { left: { type: 'text', content: '开朗' }, right: { type: 'text', content: '活泼' } }, { left: { type: 'text', content: '耐心' }, right: { type: 'text', content: '细心' } }, { left: { type: 'text', content: '踏实' }, right: { type: 'text', content: '稳重' } }], time_limit: 75 },
  ],
  // L3：反义词连线 —— 30题
  L3: [
    { id: 'cg_L3_001', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '黑暗' }, right: { type: 'text', content: '光明' } }, { left: { type: 'text', content: '寒冷' }, right: { type: 'text', content: '温暖' } }, { left: { type: 'text', content: '喜欢' }, right: { type: 'text', content: '讨厌' } }, { left: { type: 'text', content: '开始' }, right: { type: 'text', content: '结束' } }, { left: { type: 'text', content: '胜利' }, right: { type: 'text', content: '失败' } }], time_limit: 90 },
    { id: 'cg_L3_002', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '诚实' }, right: { type: 'text', content: '虚假' } }, { left: { type: 'text', content: '努力' }, right: { type: 'text', content: '懒惰' } }, { left: { type: 'text', content: '团结' }, right: { type: 'text', content: '分裂' } }, { left: { type: 'text', content: '善良' }, right: { type: 'text', content: '凶恶' } }, { left: { type: 'text', content: '谦虚' }, right: { type: 'text', content: '骄傲' } }], time_limit: 90 },
    { id: 'cg_L3_003', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '宽容' }, right: { type: 'text', content: '苛刻' } }, { left: { type: 'text', content: '勤奋' }, right: { type: 'text', content: '懈怠' } }, { left: { type: 'text', content: '慷慨' }, right: { type: 'text', content: '吝啬' } }, { left: { type: 'text', content: '坚定' }, right: { type: 'text', content: '动摇' } }, { left: { type: 'text', content: '乐观' }, right: { type: 'text', content: '悲观' } }], time_limit: 90 },
    { id: 'cg_L3_004', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '聪慧' }, right: { type: 'text', content: '愚笨' } }, { left: { type: 'text', content: '勇猛' }, right: { type: 'text', content: '懦弱' } }, { left: { type: 'text', content: '繁荣' }, right: { type: 'text', content: '衰败' } }, { left: { type: 'text', content: '和平' }, right: { type: 'text', content: '战争' } }, { left: { type: 'text', content: '自由' }, right: { type: 'text', content: '束缚' } }], time_limit: 90 },
    { id: 'cg_L3_005', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '高尚' }, right: { type: 'text', content: '卑鄙' } }, { left: { type: 'text', content: '坚毅' }, right: { type: 'text', content: '软弱' } }, { left: { type: 'text', content: '博学' }, right: { type: 'text', content: '无知' } }, { left: { type: 'text', content: '公正' }, right: { type: 'text', content: '偏颇' } }, { left: { type: 'text', content: '进步' }, right: { type: 'text', content: '退步' } }], time_limit: 90 },
    { id: 'cg_L3_006', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '创新' }, right: { type: 'text', content: '守旧' } }, { left: { type: 'text', content: '清廉' }, right: { type: 'text', content: '腐败' } }, { left: { type: 'text', content: '奉献' }, right: { type: 'text', content: '自私' } }, { left: { type: 'text', content: '包容' }, right: { type: 'text', content: '排斥' } }, { left: { type: 'text', content: '勤劳' }, right: { type: 'text', content: '懒惰' } }], time_limit: 90 },
    { id: 'cg_L3_007', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '快乐' }, right: { type: 'text', content: '痛苦' } }, { left: { type: 'text', content: '希望' }, right: { type: 'text', content: '绝望' } }, { left: { type: 'text', content: '成功' }, right: { type: 'text', content: '失败' } }, { left: { type: 'text', content: '富裕' }, right: { type: 'text', content: '贫穷' } }, { left: { type: 'text', content: '健康' }, right: { type: 'text', content: '病弱' } }], time_limit: 90 },
    { id: 'cg_L3_008', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '聪明' }, right: { type: 'text', content: '愚蠢' } }, { left: { type: 'text', content: '勤快' }, right: { type: 'text', content: '懒散' } }, { left: { type: 'text', content: '整洁' }, right: { type: 'text', content: '凌乱' } }, { left: { type: 'text', content: '安静' }, right: { type: 'text', content: '喧闹' } }, { left: { type: 'text', content: '明亮' }, right: { type: 'text', content: '黑暗' } }], time_limit: 90 },
    { id: 'cg_L3_009', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '宽阔' }, right: { type: 'text', content: '狭窄' } }, { left: { type: 'text', content: '高大' }, right: { type: 'text', content: '矮小' } }, { left: { type: 'text', content: '轻盈' }, right: { type: 'text', content: '沉重' } }, { left: { type: 'text', content: '柔软' }, right: { type: 'text', content: '坚硬' } }, { left: { type: 'text', content: '干燥' }, right: { type: 'text', content: '湿润' } }], time_limit: 90 },
    { id: 'cg_L3_010', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '增加' }, right: { type: 'text', content: '减少' } }, { left: { type: 'text', content: '扩大' }, right: { type: 'text', content: '缩小' } }, { left: { type: 'text', content: '提高' }, right: { type: 'text', content: '降低' } }, { left: { type: 'text', content: '前进' }, right: { type: 'text', content: '后退' } }, { left: { type: 'text', content: '加速' }, right: { type: 'text', content: '减速' } }], time_limit: 90 },
    { id: 'cg_L3_011', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '接受' }, right: { type: 'text', content: '拒绝' } }, { left: { type: 'text', content: '赞扬' }, right: { type: 'text', content: '批评' } }, { left: { type: 'text', content: '奖励' }, right: { type: 'text', content: '惩罚' } }, { left: { type: 'text', content: '信任' }, right: { type: 'text', content: '怀疑' } }, { left: { type: 'text', content: '尊重' }, right: { type: 'text', content: '轻视' } }], time_limit: 90 },
    { id: 'cg_L3_012', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '主动' }, right: { type: 'text', content: '被动' } }, { left: { type: 'text', content: '积极' }, right: { type: 'text', content: '消极' } }, { left: { type: 'text', content: '优点' }, right: { type: 'text', content: '缺点' } }, { left: { type: 'text', content: '长处' }, right: { type: 'text', content: '短处' } }, { left: { type: 'text', content: '正面' }, right: { type: 'text', content: '负面' } }], time_limit: 90 },
    { id: 'cg_L3_013', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '开放' }, right: { type: 'text', content: '封闭' } }, { left: { type: 'text', content: '公开' }, right: { type: 'text', content: '秘密' } }, { left: { type: 'text', content: '简单' }, right: { type: 'text', content: '复杂' } }, { left: { type: 'text', content: '清晰' }, right: { type: 'text', content: '模糊' } }, { left: { type: 'text', content: '有序' }, right: { type: 'text', content: '混乱' } }], time_limit: 90 },
    { id: 'cg_L3_014', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '古老' }, right: { type: 'text', content: '现代' } }, { left: { type: 'text', content: '传统' }, right: { type: 'text', content: '创新' } }, { left: { type: 'text', content: '保守' }, right: { type: 'text', content: '开明' } }, { left: { type: 'text', content: '落后' }, right: { type: 'text', content: '先进' } }, { left: { type: 'text', content: '陈旧' }, right: { type: 'text', content: '新颖' } }], time_limit: 90 },
    { id: 'cg_L3_015', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '深刻' }, right: { type: 'text', content: '肤浅' } }, { left: { type: 'text', content: '广博' }, right: { type: 'text', content: '狭隘' } }, { left: { type: 'text', content: '严格' }, right: { type: 'text', content: '宽松' } }, { left: { type: 'text', content: '细致' }, right: { type: 'text', content: '粗糙' } }, { left: { type: 'text', content: '精确' }, right: { type: 'text', content: '模糊' } }], time_limit: 90 },
    { id: 'cg_L3_016', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '勇敢' }, right: { type: 'text', content: '胆怯' } }, { left: { type: 'text', content: '坚强' }, right: { type: 'text', content: '脆弱' } }, { left: { type: 'text', content: '自信' }, right: { type: 'text', content: '自卑' } }, { left: { type: 'text', content: '乐观' }, right: { type: 'text', content: '悲观' } }, { left: { type: 'text', content: '开朗' }, right: { type: 'text', content: '内向' } }], time_limit: 90 },
    { id: 'cg_L3_017', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '诚信' }, right: { type: 'text', content: '欺骗' } }, { left: { type: 'text', content: '正直' }, right: { type: 'text', content: '奸诈' } }, { left: { type: 'text', content: '廉洁' }, right: { type: 'text', content: '贪腐' } }, { left: { type: 'text', content: '公平' }, right: { type: 'text', content: '不公' } }, { left: { type: 'text', content: '守信' }, right: { type: 'text', content: '失信' } }], time_limit: 90 },
    { id: 'cg_L3_018', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '热爱' }, right: { type: 'text', content: '厌恶' } }, { left: { type: 'text', content: '珍视' }, right: { type: 'text', content: '轻视' } }, { left: { type: 'text', content: '感恩' }, right: { type: 'text', content: '忘恩' } }, { left: { type: 'text', content: '宽恕' }, right: { type: 'text', content: '记恨' } }, { left: { type: 'text', content: '关爱' }, right: { type: 'text', content: '冷漠' } }], time_limit: 90 },
    { id: 'cg_L3_019', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '节俭' }, right: { type: 'text', content: '奢侈' } }, { left: { type: 'text', content: '朴素' }, right: { type: 'text', content: '华丽' } }, { left: { type: 'text', content: '节约' }, right: { type: 'text', content: '浪费' } }, { left: { type: 'text', content: '勤俭' }, right: { type: 'text', content: '挥霍' } }, { left: { type: 'text', content: '简朴' }, right: { type: 'text', content: '豪华' } }], time_limit: 90 },
    { id: 'cg_L3_020', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '团结' }, right: { type: 'text', content: '分裂' } }, { left: { type: 'text', content: '合作' }, right: { type: 'text', content: '对抗' } }, { left: { type: 'text', content: '友谊' }, right: { type: 'text', content: '敌意' } }, { left: { type: 'text', content: '和谐' }, right: { type: 'text', content: '冲突' } }, { left: { type: 'text', content: '互助' }, right: { type: 'text', content: '自私' } }], time_limit: 90 },
    { id: 'cg_L3_021', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '认真' }, right: { type: 'text', content: '马虎' } }, { left: { type: 'text', content: '细心' }, right: { type: 'text', content: '粗心' } }, { left: { type: 'text', content: '专注' }, right: { type: 'text', content: '分心' } }, { left: { type: 'text', content: '耐心' }, right: { type: 'text', content: '急躁' } }, { left: { type: 'text', content: '踏实' }, right: { type: 'text', content: '浮躁' } }], time_limit: 90 },
    { id: 'cg_L3_022', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '坚持' }, right: { type: 'text', content: '放弃' } }, { left: { type: 'text', content: '完成' }, right: { type: 'text', content: '半途' } }, { left: { type: 'text', content: '付出' }, right: { type: 'text', content: '索取' } }, { left: { type: 'text', content: '奉献' }, right: { type: 'text', content: '享受' } }, { left: { type: 'text', content: '劳动' }, right: { type: 'text', content: '享乐' } }], time_limit: 90 },
    { id: 'cg_L3_023', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '记忆' }, right: { type: 'text', content: '遗忘' } }, { left: { type: 'text', content: '铭记' }, right: { type: 'text', content: '淡忘' } }, { left: { type: 'text', content: '珍藏' }, right: { type: 'text', content: '丢弃' } }, { left: { type: 'text', content: '保留' }, right: { type: 'text', content: '舍弃' } }, { left: { type: 'text', content: '传承' }, right: { type: 'text', content: '遗弃' } }], time_limit: 90 },
    { id: 'cg_L3_024', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '建设' }, right: { type: 'text', content: '破坏' } }, { left: { type: 'text', content: '创造' }, right: { type: 'text', content: '毁灭' } }, { left: { type: 'text', content: '发展' }, right: { type: 'text', content: '衰退' } }, { left: { type: 'text', content: '兴盛' }, right: { type: 'text', content: '衰落' } }, { left: { type: 'text', content: '繁荣' }, right: { type: 'text', content: '萧条' } }], time_limit: 90 },
    { id: 'cg_L3_025', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '光荣' }, right: { type: 'text', content: '耻辱' } }, { left: { type: 'text', content: '荣誉' }, right: { type: 'text', content: '羞辱' } }, { left: { type: 'text', content: '自豪' }, right: { type: 'text', content: '惭愧' } }, { left: { type: 'text', content: '赞美' }, right: { type: 'text', content: '批评' } }, { left: { type: 'text', content: '表扬' }, right: { type: 'text', content: '批评' } }], time_limit: 90 },
    { id: 'cg_L3_026', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '理性' }, right: { type: 'text', content: '感性' } }, { left: { type: 'text', content: '客观' }, right: { type: 'text', content: '主观' } }, { left: { type: 'text', content: '抽象' }, right: { type: 'text', content: '具体' } }, { left: { type: 'text', content: '宏观' }, right: { type: 'text', content: '微观' } }, { left: { type: 'text', content: '整体' }, right: { type: 'text', content: '局部' } }], time_limit: 90 },
    { id: 'cg_L3_027', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '原因' }, right: { type: 'text', content: '结果' } }, { left: { type: 'text', content: '问题' }, right: { type: 'text', content: '答案' } }, { left: { type: 'text', content: '理论' }, right: { type: 'text', content: '实践' } }, { left: { type: 'text', content: '假设' }, right: { type: 'text', content: '验证' } }, { left: { type: 'text', content: '条件' }, right: { type: 'text', content: '结论' } }], time_limit: 90 },
    { id: 'cg_L3_028', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '坚硬' }, right: { type: 'text', content: '柔软' } }, { left: { type: 'text', content: '粗糙' }, right: { type: 'text', content: '光滑' } }, { left: { type: 'text', content: '浓厚' }, right: { type: 'text', content: '稀薄' } }, { left: { type: 'text', content: '沉重' }, right: { type: 'text', content: '轻盈' } }, { left: { type: 'text', content: '炎热' }, right: { type: 'text', content: '寒冷' } }], time_limit: 90 },
    { id: 'cg_L3_029', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '真实' }, right: { type: 'text', content: '虚假' } }, { left: { type: 'text', content: '正确' }, right: { type: 'text', content: '错误' } }, { left: { type: 'text', content: '合理' }, right: { type: 'text', content: '荒谬' } }, { left: { type: 'text', content: '科学' }, right: { type: 'text', content: '迷信' } }, { left: { type: 'text', content: '文明' }, right: { type: 'text', content: '野蛮' } }], time_limit: 90 },
    { id: 'cg_L3_030', type: 'text_text', instruction: '把反义词连起来', pairs: [{ left: { type: 'text', content: '善始' }, right: { type: 'text', content: '善终' } }, { left: { type: 'text', content: '有始' }, right: { type: 'text', content: '有终' } }, { left: { type: 'text', content: '始终' }, right: { type: 'text', content: '半途' } }, { left: { type: 'text', content: '坚守' }, right: { type: 'text', content: '背叛' } }, { left: { type: 'text', content: '忠诚' }, right: { type: 'text', content: '背叛' } }], time_limit: 90 },
  ],
}

// ─── 工具函数 ────────────────────────────────────────────────────────────────

/** Fisher-Yates 随机打乱数组（返回新数组） */
function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

/** 生成唯一 ID */
let _uid = 0
function uid() { return 'conn_' + (++_uid) + '_' + Date.now() }

export default {
  name: 'ConnectGame',

  components: { ConnectLine },

  data() {
    return {
      // 游戏配置
      difficulty: 'L1',
      taskId: null,
      currentQuestion: null,

      // 游戏状态
      phase: 'loading',       // 'loading' | 'playing' | 'result' | 'timeout'
      leftItems: [],          // [{ id, type, content, pairIndex }]
      rightItems: [],         // [{ id, type, content, pairIndex }]（随机排列）
      connections: [],        // [{ id, leftId, rightId, isCorrect }]

      // 拖动状态
      draggingLeftId: null,   // 当前正在拖动的左侧项 id
      tempLine: null,         // { fromX, fromY, toX, toY }

      // 连线层尺寸（px，由 createSelectorQuery 获取）
      lineLayerWidth: 375,
      lineLayerHeight: 600,
      lineLayerLeft: 0,       // 连线层相对页面的 left 偏移
      lineLayerTop: 0,        // 连线层相对页面的 top 偏移

      // 坐标缓存（相对于连线层）
      leftPositions: {},      // { [itemId]: { x, y } }
      rightPositions: {},     // { [itemId]: { x, y } }

      // 右侧项的点击区域（相对于页面，用于落点判断）
      rightRects: {},         // { [itemId]: { left, top, right, bottom } }

      // 计时
      timeLeft: 90,
      timerInterval: null,
      startTime: null,
      elapsedSeconds: 0,

      // 结果
      showTimeout: false,
      starsEarned: 0,
      showExitModal: false,
    }
  },

  computed: {
    totalPairs() {
      return this.leftItems.length
    },
    correctCount() {
      return this.connections.filter(c => c.isCorrect === true).length
    },
  },

  onLoad(options) {
    this.difficulty = options.difficulty || 'L1'
    this.taskId = options.task_id ? parseInt(options.task_id) : null
    this.initGame()
  },

  onUnload() {
    this._clearTimer()
  },

  methods: {
    // ── 初始化 ──────────────────────────────────────────────────────────────

    initGame() {
      this.phase = 'loading'
      this.connections = []
      this.draggingLeftId = null
      this.tempLine = null
      this.leftPositions = {}
      this.rightPositions = {}
      this.rightRects = {}
      this.showTimeout = false
      this.starsEarned = 0
      this.elapsedSeconds = 0
      this._clearTimer()

      // 取题目（随机抽取一题）
      const questions = LOCAL_QUESTIONS[this.difficulty] || LOCAL_QUESTIONS.L1
      const randomIndex = Math.floor(Math.random() * questions.length)
      this.currentQuestion = questions[randomIndex]
      this.timeLeft = this.currentQuestion.time_limit || 90

      // 构建左右侧项
      const pairs = this.currentQuestion.pairs
      this.leftItems = pairs.map((p, idx) => ({
        id: 'left_item_' + idx,
        type: p.left.type,
        content: p.left.content,
        pairIndex: idx,
      }))
      // 右侧随机打乱
      const rightRaw = pairs.map((p, idx) => ({
        id: 'right_item_' + idx,
        type: p.right.type,
        content: p.right.content,
        pairIndex: idx,
      }))
      this.rightItems = shuffle(rightRaw)

      this.phase = 'playing'
      this.startTime = Date.now()
      this._startTimer()

      // 延迟获取坐标（等待 DOM 渲染完成）
      setTimeout(() => { this._queryPositions() }, 300)
    },

    // ── 坐标查询 ─────────────────────────────────────────────────────────────

    /**
     * 使用 uni.createSelectorQuery 获取各项的中心坐标和连线层的位置
     * 坐标转换为相对于连线层的坐标，供 ConnectLine 组件使用
     */
    _queryPositions() {
      const query = uni.createSelectorQuery().in(this)

      // 先查询连线层的位置
      query.select('#line-layer-wrapper').boundingClientRect((layerRect) => {
        if (!layerRect) return

        this.lineLayerLeft = layerRect.left
        this.lineLayerTop = layerRect.top
        this.lineLayerWidth = layerRect.width
        this.lineLayerHeight = layerRect.height

        // 查询左侧项坐标
        const leftQuery = uni.createSelectorQuery().in(this)
        this.leftItems.forEach(item => {
          leftQuery.select('#left_' + item.id).boundingClientRect()
        })
        leftQuery.exec((results) => {
          const newLeftPos = {}
          results.forEach((rect, idx) => {
            if (rect) {
              const item = this.leftItems[idx]
              newLeftPos[item.id] = {
                x: rect.left + rect.width / 2 - this.lineLayerLeft,
                y: rect.top + rect.height / 2 - this.lineLayerTop,
              }
            }
          })
          this.leftPositions = newLeftPos

          // 查询右侧项坐标
          const rightQuery = uni.createSelectorQuery().in(this)
          this.rightItems.forEach(item => {
            rightQuery.select('#right_' + item.id).boundingClientRect()
          })
          rightQuery.exec((rResults) => {
            const newRightPos = {}
            const newRightRects = {}
            rResults.forEach((rect, idx) => {
              if (rect) {
                const item = this.rightItems[idx]
                newRightPos[item.id] = {
                  x: rect.left + rect.width / 2 - this.lineLayerLeft,
                  y: rect.top + rect.height / 2 - this.lineLayerTop,
                }
                // 保存页面绝对坐标用于落点判断
                newRightRects[item.id] = {
                  left: rect.left,
                  top: rect.top,
                  right: rect.left + rect.width,
                  bottom: rect.top + rect.height,
                }
              }
            })
            this.rightPositions = newRightPos
            this.rightRects = newRightRects
          })
        })
      }).exec()
    },

    // ── 触摸事件 ─────────────────────────────────────────────────────────────

    onTouchStart(event, leftItem) {
      if (this.phase !== 'playing') return

      const touch = event.touches[0]
      if (!touch) return

      this.draggingLeftId = leftItem.id

      // 起点：左侧项中心（相对连线层）
      const lp = this.leftPositions[leftItem.id]
      const fromX = lp ? lp.x : (touch.clientX - this.lineLayerLeft)
      const fromY = lp ? lp.y : (touch.clientY - this.lineLayerTop)

      this.tempLine = {
        fromX,
        fromY,
        toX: touch.clientX - this.lineLayerLeft,
        toY: touch.clientY - this.lineLayerTop,
      }
    },

    onPageTouchMove(event) {
      if (!this.draggingLeftId || this.phase !== 'playing') return
      const touch = event.touches[0]
      if (!touch || !this.tempLine) return

      this.tempLine = {
        ...this.tempLine,
        toX: touch.clientX - this.lineLayerLeft,
        toY: touch.clientY - this.lineLayerTop,
      }
    },

    onPageTouchEnd(event) {
      if (!this.draggingLeftId || this.phase !== 'playing') return

      const touch = event.changedTouches[0]
      if (!touch) {
        this._cancelDrag()
        return
      }

      const pageX = touch.clientX
      const pageY = touch.clientY

      // 判断落点是否在某个右侧项区域内
      const hitItem = this._findRightItemAt(pageX, pageY)

      if (hitItem) {
        this._handleDrop(this.draggingLeftId, hitItem)
      } else {
        // 落点不在任何右侧项区域，取消连线
        this._cancelDrag()
      }
    },

    /** 查找坐标 (x, y) 落在哪个右侧项区域内 */
    _findRightItemAt(x, y) {
      for (const item of this.rightItems) {
        const rect = this.rightRects[item.id]
        if (rect && x >= rect.left && x <= rect.right && y >= rect.top && y <= rect.bottom) {
          return item
        }
      }
      return null
    },

    /** 处理连线落点 */
    _handleDrop(leftId, rightItem) {
      // 若该左侧项已有连线，先移除旧连线
      const existingConn = this.connections.find(c => c.leftId === leftId)
      if (existingConn) {
        this.connections = removeConnection(this.connections, existingConn.id)
      }

      // 若该右侧项已被其他左侧项连线，也移除旧连线
      const existingRightConn = this.connections.find(c => c.rightId === rightItem.id)
      if (existingRightConn) {
        this.connections = removeConnection(this.connections, existingRightConn.id)
      }

      // 判断是否正确：左侧项的 pairIndex 与右侧项的 pairIndex 相同
      const leftItem = this.leftItems.find(i => i.id === leftId)
      const isCorrect = leftItem && leftItem.pairIndex === rightItem.pairIndex

      // 建立新连线
      const newConn = {
        id: uid(),
        leftId,
        rightId: rightItem.id,
        isCorrect: isCorrect ? true : false,
      }
      this.connections = [...this.connections, newConn]

      // 播放音效
      if (isCorrect) {
        AudioManager.playSFX('connect')
      } else {
        AudioManager.playSFX('wrong')
      }

      this._cancelDrag()

      // 检查是否全部正确完成
      this._checkAllCorrect()
    },

    _cancelDrag() {
      this.draggingLeftId = null
      this.tempLine = null
    },

    // ── 连线点击删除 ─────────────────────────────────────────────────────────

    onLineClick(connId) {
      if (this.phase !== 'playing') return
      this.connections = removeConnection(this.connections, connId)
    },

    // ── 提交按钮 ─────────────────────────────────────────────────────────────

    onSubmitClick() {
      if (this.correctCount >= this.totalPairs) {
        this._finishGame()
      }
    },

    // ── 完成检测 ─────────────────────────────────────────────────────────────

    _checkAllCorrect() {
      // 所有左侧项均已正确连线
      const allCorrect = this.leftItems.every(item =>
        this.connections.some(c => c.leftId === item.id && c.isCorrect === true)
      )
      if (allCorrect) {
        this._finishGame()
      }
    },

    async _finishGame() {
      this._clearTimer()
      this.elapsedSeconds = Math.round((Date.now() - this.startTime) / 1000)

      const accuracyRate = this.totalPairs > 0 ? this.correctCount / this.totalPairs : 0
      this.starsEarned = calcConnectGameStars(accuracyRate)

      AudioManager.playSFX('complete')
      this.phase = 'result'
      await this._submitResult()
    },

    async _submitResult() {
      const accuracyRate = this.totalPairs > 0 ? this.correctCount / this.totalPairs : 0
      const accuracy = Math.round(accuracyRate * 100)
      const payload = buildConnectGamePayload({
        taskId: this.taskId,
        difficulty: this.difficulty,
        starsEarned: this.starsEarned,
        durationSeconds: this.elapsedSeconds,
        totalPairs: this.totalPairs,
        correctPairs: this.correctCount,
        accuracyRate,
      })

      if (this.taskId) {
        try {
          await completeTask(this.taskId, payload)
        } catch (e) {
          enqueueRecord({ taskId: this.taskId, payload })
        }
      } else {
        // 从挑战tab直接进入，没有task_id，自动创建并完成任务以记录星星
        try {
          const child = getCurrentChild()
          if (child?.id) {
            const task = await createTask({
              child_id: child.id,
              task_type: 'connect_game',
              task_name: '连一连挑战',
              scheduled_date: new Date().toISOString().split('T')[0],
            })
            await completeTask(task.id, { ...payload, task_id: task.id })
          }
        } catch (e) { console.warn('自动创建任务失败', e) }
      }

      // 保存结果供结算页使用（与前6种游戏格式对齐）
      uni.setStorageSync('last_training_result', {
        game_type: 'connect_game',
        correct_count: this.correctCount,
        total_count: this.totalPairs,
        accuracy,
        stars: this.starsEarned,
        mode: 'training',
      })
    },

    // ── 超时 ─────────────────────────────────────────────────────────────────

    _onTimeout() {
      if (this.phase !== 'playing') return
      this.phase = 'timeout'
      this.showTimeout = true
    },

    // ── 计时器 ───────────────────────────────────────────────────────────────

    _startTimer() {
      this._clearTimer()
      this.timerInterval = setInterval(() => {
        this.timeLeft--
        if (this.timeLeft <= 0) {
          this._clearTimer()
          this._onTimeout()
        }
      }, 1000)
    },

    _clearTimer() {
      if (this.timerInterval) {
        clearInterval(this.timerInterval)
        this.timerInterval = null
      }
    },

    // ── 辅助：连线状态查询 ───────────────────────────────────────────────────

    isLeftConnected(leftId) {
      return this.connections.some(c => c.leftId === leftId)
    },
    isLeftCorrect(leftId) {
      return this.connections.some(c => c.leftId === leftId && c.isCorrect === true)
    },
    isLeftWrong(leftId) {
      return this.connections.some(c => c.leftId === leftId && c.isCorrect === false)
    },
    isRightConnected(rightId) {
      return this.connections.some(c => c.rightId === rightId)
    },
    isRightCorrect(rightId) {
      return this.connections.some(c => c.rightId === rightId && c.isCorrect === true)
    },
    isRightWrong(rightId) {
      return this.connections.some(c => c.rightId === rightId && c.isCorrect === false)
    },

    // ── 导航 ─────────────────────────────────────────────────────────────────

    restartGame() {
      this.showTimeout = false
      this.initGame()
    },

    finishGame() {
      uni.redirectTo({ url: '/pages/child/training-reward/index' })
    },

    goBack() {
      this._clearTimer()
      uni.navigateBack({ delta: 1 })
    },

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
/* ── 页面容器 ─────────────────────────────────────────────────────────────── */
.page-container {
  min-height: 100vh;
  background: linear-gradient(160deg, #F0FDF4 0%, #DCFCE7 100%);
  display: flex;
  flex-direction: column;
  width: 100%;
  box-sizing: border-box;
  /* 将 touchmove/touchend 绑定到页面容器，捕获拖动事件 */
}

/* ── 顶部栏 ───────────────────────────────────────────────────────────────── */
.top-bar {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 56rpx 32rpx 20rpx;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 2rpx 12rpx rgba(34, 197, 94, 0.1);
  flex-shrink: 0;
  gap: 16rpx;
}

.back-btn {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: #DCFCE7;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #BBF7D0;
  flex-shrink: 0;
}
.back-btn:active { transform: scale(0.92); }
.back-btn .ph { font-size: 32rpx; color: #16A34A; }

.title-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}
.game-title {
  font-size: 32rpx;
  font-weight: 800;
  color: #15803D;
}
.game-instruction {
  font-size: 24rpx;
  color: #4ADE80;
  font-weight: 600;
}

.timer-chip {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6rpx;
  background: #DCFCE7;
  padding: 10rpx 18rpx;
  border-radius: 24rpx;
  border: 2rpx solid #BBF7D0;
  flex-shrink: 0;
}
.timer-chip .ph { font-size: 26rpx; color: #16A34A; }
.timer-val { font-size: 26rpx; font-weight: 800; color: #15803D; }
.top-right-area {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 12rpx;
  flex-shrink: 0;
}

.exit-btn {
  width: 64rpx; height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 107, 107, 0.1);
  border: 2rpx solid rgba(255, 107, 107, 0.2);
  display: flex; align-items: center; justify-content: center;
}
.exit-btn .ph { font-size: 28rpx; color: #FF6B6B; }

/* 退出确认弹窗 */
.exit-modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  z-index: 9999;
  display: flex; justify-content: center; align-items: center;
}
.exit-modal-content {
  background: #FFFFFF;
  width: 85%; max-width: 640rpx;
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  display: flex; flex-direction: column; align-items: center;
  box-shadow: 0 16rpx 48rpx rgba(0,0,0,0.15);
}
.exit-modal-icon {
  width: 112rpx; height: 112rpx;
  border-radius: 28rpx;
  background: linear-gradient(135deg, #FFF9C4, #FFE082);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 28rpx;
}
.exit-modal-icon .ph { font-size: 56rpx; color: #F57F17; }
.exit-modal-title { font-size: 36rpx; font-weight: 800; color: #2D3748; margin-bottom: 12rpx; }
.exit-modal-desc { font-size: 26rpx; color: #718096; text-align: center; margin-bottom: 36rpx; font-weight: 500; line-height: 1.6; }
.exit-modal-btn {
  width: 100%; border-radius: 16rpx;
  padding: 28rpx; font-size: 28rpx; font-weight: 700;
  margin-bottom: 16rpx; transition: all 0.2s;
}
.exit-modal-btn.outline {
  background: #F5F5F5; color: #718096;
}
.exit-modal-btn.primary {
  background: linear-gradient(135deg, #4F9EF8, #3B82F6);
  color: #FFFFFF;
  box-shadow: 0 4rpx 12rpx rgba(59,130,246,0.25);
}

/* ── 游戏区域 ─────────────────────────────────────────────────────────────── */
.game-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24rpx 0 0;
  width: 100%;
  box-sizing: border-box;
}

/* 三列布局 */
.columns-wrapper {
  flex: 1;
  display: flex;
  flex-direction: row;
  align-items: stretch;
  position: relative;
  padding: 0 16rpx;
  gap: 0;
}

/* 左右侧项列 */
.items-col {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  gap: 20rpx;
  padding: 16rpx 0;
  z-index: 20;
  flex-shrink: 0;
  width: 160rpx;
}

.items-left { align-items: flex-end; }
.items-right { align-items: flex-start; }

/* 连线层（中间区域，绝对定位覆盖） */
.line-layer-wrapper {
  flex: 1;
  position: relative;
  z-index: 10;
  min-width: 0;
}

/* 单个项卡片 */
.item-card {
  width: 140rpx;
  min-height: 100rpx;
  border-radius: 24rpx;
  background: #FFFFFF;
  border: 3rpx solid #BBF7D0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16rpx 12rpx;
  box-shadow: 0 4rpx 12rpx rgba(34, 197, 94, 0.12);
  transition: all 0.2s;
  cursor: pointer;
  user-select: none;
}

.item-card:active { transform: scale(0.95); }

/* 左侧项：右侧有连接点视觉提示 */
.item-left {
  border-right: 5rpx solid #22C55E;
}

/* 右侧项：左侧有连接点视觉提示 */
.item-right {
  border-left: 5rpx solid #22C55E;
}

/* 已连线状态 */
.item-connected {
  border-color: #3B82F6;
  background: #EFF6FF;
}

/* 正确连线 */
.item-correct {
  border-color: #22C55E !important;
  background: #F0FDF4 !important;
  box-shadow: 0 0 0 3rpx rgba(34, 197, 94, 0.3), 0 4rpx 12rpx rgba(34, 197, 94, 0.2) !important;
}

/* 错误连线 */
.item-wrong {
  border-color: #EF4444 !important;
  background: #FEF2F2 !important;
  box-shadow: 0 0 0 3rpx rgba(239, 68, 68, 0.3), 0 4rpx 12rpx rgba(239, 68, 68, 0.2) !important;
}

/* 拖动中的左侧项 */
.item-dragging {
  transform: scale(1.05);
  box-shadow: 0 8rpx 24rpx rgba(34, 197, 94, 0.35) !important;
  border-color: #16A34A !important;
  z-index: 30;
}

/* 项内容 */
.item-emoji {
  font-size: 64rpx;
  line-height: 1;
}
.item-text {
  font-size: 44rpx;
  font-weight: 800;
  color: #15803D;
  text-align: center;
  line-height: 1.2;
}

/* ── 底部栏 ───────────────────────────────────────────────────────────────── */
.bottom-bar {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 32rpx 40rpx;
  background: rgba(255, 255, 255, 0.9);
  border-top: 2rpx solid #BBF7D0;
  flex-shrink: 0;
}

.progress-info {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8rpx;
}
.progress-info .ph { font-size: 28rpx; color: #22C55E; }
.progress-text { font-size: 28rpx; font-weight: 700; color: #15803D; }

.submit-btn {
  background: linear-gradient(135deg, #4ADE80, #22C55E);
  color: #FFFFFF;
  border-radius: 24rpx;
  padding: 20rpx 40rpx;
  font-size: 28rpx;
  font-weight: 700;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(34, 197, 94, 0.35);
  border: none;
}
.submit-btn:active { transform: scale(0.97); }
.submit-btn[disabled] {
  background: #D1FAE5;
  color: #6EE7B7;
  box-shadow: none;
}
.submit-btn .ph { font-size: 28rpx; }

/* ── 加载中 ───────────────────────────────────────────────────────────────── */
.loading-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
.loading-text {
  font-size: 32rpx;
  color: #22C55E;
  font-weight: 600;
}

/* ── 弹窗 ─────────────────────────────────────────────────────────────────── */
.overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-card {
  background: #FFFFFF;
  width: 88%;
  max-width: 620rpx;
  border-radius: 40rpx;
  padding: 52rpx 40rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20rpx;
  animation: popIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes popIn {
  from { opacity: 0; transform: scale(0.8); }
  to { opacity: 1; transform: scale(1); }
}

.timeout-card { border-top: 8rpx solid #F59E0B; }
.result-card { border-top: 8rpx solid #22C55E; }

.modal-emoji { font-size: 88rpx; line-height: 1; }
.modal-title { font-size: 44rpx; font-weight: 900; color: #2D3748; }
.modal-desc { font-size: 28rpx; color: #718096; font-weight: 500; text-align: center; }

.modal-btn {
  width: 100%;
  border-radius: 24rpx;
  padding: 28rpx;
  font-size: 30rpx;
  font-weight: 700;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  border: none;
}
.modal-btn:active { transform: scale(0.97); }

.btn-retry {
  background: linear-gradient(135deg, #4ADE80, #22C55E);
  color: #FFFFFF;
  box-shadow: 0 4rpx 16rpx rgba(34, 197, 94, 0.35);
}
.btn-back { background: #F3F4F6; color: #6B7280; margin-top: -8rpx; }
.btn-finish {
  background: linear-gradient(135deg, #4ADE80, #22C55E);
  color: #FFFFFF;
  box-shadow: 0 4rpx 16rpx rgba(34, 197, 94, 0.35);
}
.btn-finish .ph { font-size: 30rpx; }
.btn-retry-sm { background: #DCFCE7; color: #16A34A; margin-top: -8rpx; }

/* 结果弹窗内容 */
.result-emoji { font-size: 96rpx; line-height: 1; }
.result-title { font-size: 44rpx; font-weight: 900; color: #15803D; }

.result-stars {
  display: flex;
  flex-direction: row;
  gap: 8rpx;
}
.result-star { font-size: 48rpx; opacity: 0.2; transition: all 0.3s; }
.result-star.earned {
  opacity: 1;
  animation: starPop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
@keyframes starPop {
  from { transform: scale(0); }
  to { transform: scale(1); }
}

.result-stats {
  display: flex;
  flex-direction: row;
  align-items: center;
  background: #F0FDF4;
  border-radius: 20rpx;
  padding: 20rpx 32rpx;
  width: 100%;
}
.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
}
.stat-num { font-size: 44rpx; font-weight: 900; color: #22C55E; }
.stat-label { font-size: 22rpx; color: #4ADE80; font-weight: 600; }
.stat-divider { width: 2rpx; height: 60rpx; background: #BBF7D0; }
</style>
