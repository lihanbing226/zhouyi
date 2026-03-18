<template>
  <div class="bazi-chart">
    <table class="pillar-table">
      <thead>
        <tr>
          <th>年柱</th>
          <th>月柱</th>
          <th>日柱</th>
          <th>时柱</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td v-for="(pillar, i) in pillars" :key="i">
            <GanzhiPill :gan="pillar.gan" :zhi="pillar.zhi" />
          </td>
        </tr>
      </tbody>
    </table>

    <div class="day-master" v-if="dayMaster">
      <span class="dm-label">日主</span>
      <span class="dm-value">{{ dayMaster }}</span>
      <span class="dm-strength" :class="strength === '身强' ? 'strong' : 'weak'">
        {{ strength }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BaziResponse } from '@/types/bazi'
import GanzhiPill from './GanzhiPill.vue'

const props = defineProps<{
  bazi: BaziResponse
}>()

const pillars = computed(() => [
  { gan: props.bazi.year_gan, zhi: props.bazi.year_zhi },
  { gan: props.bazi.month_gan, zhi: props.bazi.month_zhi },
  { gan: props.bazi.day_gan, zhi: props.bazi.day_zhi },
  { gan: props.bazi.hour_gan, zhi: props.bazi.hour_zhi },
])

const dayMaster = computed(() => props.bazi.day_master)
const strength = computed(() => props.bazi.strength)
</script>

<style scoped>
.bazi-chart {
  background: #111118;
  border: 1px solid #2a2a35;
  border-radius: 12px;
  padding: 24px;
}

.pillar-table {
  width: 100%;
  border-collapse: collapse;
  text-align: center;
}

.pillar-table th {
  color: #a09070;
  font-size: 14px;
  font-weight: 400;
  padding-bottom: 16px;
}

.pillar-table td {
  padding: 8px;
}

.day-master {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #2a2a35;
}

.dm-label {
  color: #a09070;
  font-size: 14px;
}

.dm-value {
  color: #c9a84c;
  font-size: 18px;
  font-weight: 600;
}

.dm-strength {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
}

.dm-strength.strong {
  background: rgba(76, 175, 80, 0.1);
  color: #66bb6a;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.dm-strength.weak {
  background: rgba(44, 95, 138, 0.1);
  color: #5c9fd4;
  border: 1px solid rgba(44, 95, 138, 0.3);
}
</style>
