/**八字命盘相关类型定义 */

export interface BaziRequest {
  birth_datetime: Date
  gender?: 'M' | 'F'
  location?: string
}

export interface BaziResponse {
  id: string
  year_gan: string
  year_zhi: string
  month_gan: string
  month_zhi: string
  day_gan: string
  day_zhi: string
  hour_gan: string
  hour_zhi: string
  day_master: string
  strength: '身强' | '身弱'
  wuxing_score: Record<string, number>
  analysis: string
  luck_outlook: string
}

export interface Pillar {
  gan: string
  zhi: string
}

export interface WuxingElement {
  name: string
  count: number
  wuxing: '金' | '木' | '水' | '火' | '土'
}
