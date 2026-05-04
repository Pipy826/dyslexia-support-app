/**
 * AudioManager 单例
 * 负责儿童端 BGM 背景音乐与 SFX 游戏音效的统一管理
 * 适配 UniApp（微信小程序 + H5）环境
 *
 * 功能：
 *  - BGM 播放/停止/切换/音量控制
 *  - SFX 按事件类型播放
 *  - BGM 音量闪避（Ducking）：SFX 触发时降低 BGM 音量，播完后线性恢复
 *  - 偏好持久化（uni.setStorageSync / uni.getStorageSync）
 *  - 设备静音模式检测
 */

// ─── 音频资源路径 ────────────────────────────────────────────────────────────

/** BGM 曲目列表 */
const BGM_TRACKS = [
  '/static/audio/bgm/bgm_01.mp3',
  '/static/audio/bgm/bgm_02.mp3',
];

/** SFX 事件 → 文件路径映射 */
const SFX_MAP = {
  correct:  '/static/audio/sfx/correct.mp3',
  wrong:    '/static/audio/sfx/wrong.mp3',
  complete: '/static/audio/sfx/complete.mp3',
  click:    '/static/audio/sfx/click.mp3',
  flip:     '/static/audio/sfx/flip.mp3',
  connect:  '/static/audio/sfx/connect.mp3',
};

/** 本地存储 key */
const STORAGE_KEY = 'audio_preferences';

/** BGM 默认音量 */
const BGM_DEFAULT_VOLUME = 0.6;

/** BGM 闪避时的目标音量 */
const BGM_DUCK_VOLUME = 0.3;

/** SFX 播完后恢复 BGM 音量的总时长（ms） */
const DUCK_RESTORE_DURATION = 500;

/** 音量恢复的步进间隔（ms） */
const DUCK_RESTORE_INTERVAL = 50;

// ─── AudioManager 单例对象 ───────────────────────────────────────────────────

const AudioManager = {
  // ── 状态 ──────────────────────────────────────────────────────────────────

  /** BGM 是否开启 */
  bgmEnabled: true,

  /** SFX 是否开启 */
  sfxEnabled: true,

  /** 当前 BGM 目标音量（用户设置值，不受 ducking 影响） */
  bgmVolume: BGM_DEFAULT_VOLUME,

  /** 当前播放的 BGM 曲目索引 */
  _currentTrackIndex: 0,

  /** BGM InnerAudioContext 实例 */
  _bgmContext: null,

  /** 音量恢复定时器 ID */
  _duckRestoreTimer: null,

  /** 当前 BGM 实际播放音量（受 ducking 影响） */
  _currentBgmVolume: BGM_DEFAULT_VOLUME,

  // ── BGM 控制 ──────────────────────────────────────────────────────────────

  /**
   * 播放指定曲目的 BGM
   * @param {number} [trackIndex=0] - 曲目索引（0 或 1）
   */
  playBGM(trackIndex = 0) {
    if (!this.bgmEnabled) return;

    // H5 环境下，若音频文件不存在则静默跳过，避免 NotSupportedError
    // #ifdef H5
    if (typeof window !== 'undefined') {
      const src = BGM_TRACKS[Math.max(0, Math.min(trackIndex, BGM_TRACKS.length - 1))];
      // 用 fetch HEAD 检测文件是否存在（异步，不阻塞）
      fetch(src, { method: 'HEAD' }).then(r => {
        if (r.ok) this._doPlayBGM(trackIndex);
        // 文件不存在时静默跳过
      }).catch(() => { /* 网络错误或文件不存在，静默跳过 */ });
      return;
    }
    // #endif

    this._doPlayBGM(trackIndex);
  },

  /** 实际执行 BGM 播放（内部方法） */
  _doPlayBGM(trackIndex = 0) {
    // 静音模式检测（仅在小程序端有效）
    try {
      const sysInfo = uni.getSystemInfoSync();
      if (sysInfo.platform !== 'h5') {
        const knownPlatforms = ['ios', 'android', 'devtools', 'windows', 'mac'];
        if (!knownPlatforms.includes(sysInfo.platform)) return;
      }
    } catch (e) { /* 忽略 */ }

    const safeIndex = Math.max(0, Math.min(trackIndex, BGM_TRACKS.length - 1));
    this._currentTrackIndex = safeIndex;

    if (this._bgmContext) {
      try { this._bgmContext.stop(); this._bgmContext.destroy(); } catch (e) { /* 忽略 */ }
      this._bgmContext = null;
    }

    try {
      const ctx = uni.createInnerAudioContext();
      ctx.src = BGM_TRACKS[safeIndex];
      ctx.loop = true;
      ctx.volume = this.bgmVolume;
      ctx.autoplay = false;

      ctx.onError(() => { /* BGM 加载失败，静默跳过 */ });

      // H5 play() 返回 Promise，捕获 NotAllowedError / NotSupportedError
      const playResult = ctx.play();
      if (playResult && typeof playResult.catch === 'function') {
        playResult.catch(() => { /* 浏览器策略阻止或文件缺失，静默跳过 */ });
      }
      this._bgmContext = ctx;
      this._currentBgmVolume = this.bgmVolume;
    } catch (e) { /* 创建上下文失败，静默跳过 */ }
  },

  /**
   * 停止 BGM 播放
   */
  stopBGM() {
    if (this._bgmContext) {
      try {
        this._bgmContext.stop();
        this._bgmContext.destroy();
      } catch (e) {
        // 忽略
      }
      this._bgmContext = null;
    }
    this._clearDuckRestoreTimer();
  },

  /**
   * 切换 BGM 开关状态
   * 关闭时停止播放；开启时从当前曲目继续播放
   */
  toggleBGM() {
    this.bgmEnabled = !this.bgmEnabled;
    if (this.bgmEnabled) {
      this.playBGM(this._currentTrackIndex);
    } else {
      this.stopBGM();
    }
    this.savePreferences();
  },

  /**
   * 设置 BGM 音量
   * @param {number} volume - 目标音量，范围 [0, 1]
   */
  setBGMVolume(volume) {
    const clamped = Math.min(1, Math.max(0, volume));
    this.bgmVolume = clamped;
    this._currentBgmVolume = clamped;
    if (this._bgmContext) {
      try {
        this._bgmContext.volume = clamped;
      } catch (e) {
        // 忽略
      }
    }
  },

  // ── SFX 控制 ──────────────────────────────────────────────────────────────

  /**
   * 播放指定事件类型的音效
   * 触发时将 BGM 音量降至 0.3（ducking），SFX 播完后 500ms 内线性恢复
   * @param {string} eventType - 事件类型：'correct'|'wrong'|'complete'|'click'|'flip'|'connect'
   */
  playSFX(eventType) {
    if (!this.sfxEnabled) return;

    const src = SFX_MAP[eventType];
    if (!src) return;

    // H5 环境下先检测文件是否存在，避免 NotSupportedError
    // #ifdef H5
    if (typeof window !== 'undefined') {
      fetch(src, { method: 'HEAD' }).then(r => {
        if (r.ok) this._doPlaySFX(src);
      }).catch(() => { /* 文件不存在，静默跳过 */ });
      return;
    }
    // #endif

    this._doPlaySFX(src);
  },

  /** 实际执行 SFX 播放（内部方法） */
  _doPlaySFX(src) {
    try {
      const sfxCtx = uni.createInnerAudioContext();
      sfxCtx.src = src;
      sfxCtx.volume = 1.0;
      sfxCtx.autoplay = false;

      sfxCtx.onError(() => {
        try { sfxCtx.destroy(); } catch (e) { /* 忽略 */ }
      });

      this._duckBGM();

      sfxCtx.onEnded(() => {
        this._restoreBGMVolume();
        try { sfxCtx.destroy(); } catch (e) { /* 忽略 */ }
      });

      const playResult = sfxCtx.play();
      if (playResult && typeof playResult.catch === 'function') {
        playResult.catch(() => { /* 静默跳过 */ });
      }
    } catch (e) { /* 创建 SFX 上下文失败，静默跳过 */ }
  },

  // ── 偏好持久化 ────────────────────────────────────────────────────────────

  /**
   * 将当前 BGM/SFX 开关状态持久化至本地存储
   */
  savePreferences() {
    try {
      uni.setStorageSync(STORAGE_KEY, {
        bgmEnabled: this.bgmEnabled,
        sfxEnabled: this.sfxEnabled,
      });
    } catch (e) {
      // 存储失败，静默跳过
    }
  },

  /**
   * 从本地存储读取并应用音频偏好
   * @returns {{ bgmEnabled: boolean, sfxEnabled: boolean }}
   */
  loadPreferences() {
    try {
      const prefs = uni.getStorageSync(STORAGE_KEY);
      if (prefs && typeof prefs === 'object') {
        if (typeof prefs.bgmEnabled === 'boolean') {
          this.bgmEnabled = prefs.bgmEnabled;
        }
        if (typeof prefs.sfxEnabled === 'boolean') {
          this.sfxEnabled = prefs.sfxEnabled;
        }
      }
    } catch (e) {
      // 读取失败，使用默认值
    }
    return {
      bgmEnabled: this.bgmEnabled,
      sfxEnabled: this.sfxEnabled,
    };
  },

  /**
   * 切换 SFX 开关状态
   */
  toggleSFX() {
    this.sfxEnabled = !this.sfxEnabled;
    this.savePreferences();
  },

  // ── 内部辅助方法 ──────────────────────────────────────────────────────────

  /**
   * BGM 音量闪避：将 BGM 音量立即降至 BGM_DUCK_VOLUME
   * @private
   */
  _duckBGM() {
    if (!this._bgmContext) return;
    // 取消正在进行的恢复动画
    this._clearDuckRestoreTimer();
    this._currentBgmVolume = BGM_DUCK_VOLUME;
    try {
      this._bgmContext.volume = BGM_DUCK_VOLUME;
    } catch (e) {
      // 忽略
    }
  },

  /**
   * 在 DUCK_RESTORE_DURATION ms 内线性恢复 BGM 音量至用户设置值
   * @private
   */
  _restoreBGMVolume() {
    if (!this._bgmContext) return;

    this._clearDuckRestoreTimer();

    const startVolume = this._currentBgmVolume;
    const targetVolume = this.bgmVolume;

    // 已经是目标音量，无需恢复
    if (startVolume >= targetVolume) {
      this._currentBgmVolume = targetVolume;
      try { this._bgmContext.volume = targetVolume; } catch (e) { /* 忽略 */ }
      return;
    }

    const steps = Math.ceil(DUCK_RESTORE_DURATION / DUCK_RESTORE_INTERVAL);
    const volumeStep = (targetVolume - startVolume) / steps;
    let currentStep = 0;

    this._duckRestoreTimer = setInterval(() => {
      currentStep++;
      const newVolume = Math.min(targetVolume, startVolume + volumeStep * currentStep);
      this._currentBgmVolume = newVolume;
      if (this._bgmContext) {
        try {
          this._bgmContext.volume = newVolume;
        } catch (e) {
          // 忽略
        }
      }
      if (currentStep >= steps || newVolume >= targetVolume) {
        this._clearDuckRestoreTimer();
        this._currentBgmVolume = targetVolume;
        if (this._bgmContext) {
          try { this._bgmContext.volume = targetVolume; } catch (e) { /* 忽略 */ }
        }
      }
    }, DUCK_RESTORE_INTERVAL);
  },

  /**
   * 清除音量恢复定时器
   * @private
   */
  _clearDuckRestoreTimer() {
    if (this._duckRestoreTimer !== null) {
      clearInterval(this._duckRestoreTimer);
      this._duckRestoreTimer = null;
    }
  },
};

// ─── 导出 ────────────────────────────────────────────────────────────────────

export default AudioManager;
export { AudioManager, SFX_MAP, BGM_TRACKS };
