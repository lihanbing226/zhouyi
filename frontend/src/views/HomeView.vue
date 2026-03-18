<template>
  <div class="home-view">
    <section class="hero">
      <h1 class="hero-title">周易</h1>
      <p class="hero-subtitle">古老智慧 &middot; 现代演绎</p>
      <p class="hero-desc">
        融合传统周易六十四卦与八字命理，借助现代技术为您解惑指引。
      </p>
      <div class="hero-actions">
        <router-link to="/divination" class="action-btn primary">
          开始卜卦
        </router-link>
        <router-link to="/bazi" class="action-btn secondary">
          八字排盘
        </router-link>
      </div>
    </section>

    <section class="features">
      <div class="feature-card" v-for="feature in features" :key="feature.title">
        <div class="feature-icon">{{ feature.icon }}</div>
        <h3 class="feature-title">{{ feature.title }}</h3>
        <p class="feature-desc">{{ feature.desc }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const features = [
  {
    icon: '☇',
    title: '铜钱卜卦',
    desc: '虚拟三枚铜钱，六次投掷得出卦象，配合 AI 深度解读。',
  },
  {
    icon: '☰',
    title: '八字命盘',
    desc: '根据出生时辰排出四柱八字，分析五行旺衰与命理格局。',
  },
  {
    icon: '📊',
    title: '数据洞察',
    desc: '汇聚卜卦与命盘数据，以可视化看板呈现趋势与统计。',
  },
]
</script>

<style scoped>
.home-view {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 40px;
}

.hero {
  text-align: center;
  max-width: 600px;
  margin-bottom: 64px;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  color: #c9a84c;
  letter-spacing: 8px;
  margin-bottom: 12px;
}

.hero-subtitle {
  font-size: 18px;
  color: #a09070;
  letter-spacing: 4px;
  margin-bottom: 24px;
}

.hero-desc {
  font-size: 16px;
  color: #c0b8a8;
  line-height: 1.8;
  margin-bottom: 36px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.action-btn {
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 16px;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
}

.action-btn.primary {
  background: linear-gradient(135deg, #c9a84c, #a0863d);
  color: #0a0a0f;
  font-weight: 600;
}

.action-btn.primary:hover {
  box-shadow: 0 0 20px rgba(201, 168, 76, 0.3);
  transform: translateY(-1px);
}

.action-btn.secondary {
  border: 1px solid rgba(201, 168, 76, 0.4);
  color: #c9a84c;
}

.action-btn.secondary:hover {
  background: rgba(201, 168, 76, 0.1);
  border-color: #c9a84c;
}

.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  width: 100%;
  max-width: 900px;
}

.feature-card {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 32px 24px;
  text-align: center;
  transition: all 0.3s ease;
}

.feature-card:hover {
  border-color: rgba(201, 168, 76, 0.3);
  box-shadow: 0 4px 20px rgba(201, 168, 76, 0.08);
}

.feature-icon {
  font-size: 36px;
  margin-bottom: 16px;
}

.feature-title {
  font-size: 18px;
  color: #e8dcc8;
  margin-bottom: 12px;
}

.feature-desc {
  font-size: 14px;
  color: #a09070;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 40px;
  }

  .features {
    grid-template-columns: 1fr;
  }

  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
}
</style>
