/**卜卦相关类型定义 */

export interface DivinationRequest {
  question: string
  method: 'coins' | 'yarrow'
  yao_sequence?: string
}

export interface DivinationResponse {
  id: string
  hexagram_num: number
  hexagram_name: string
  yao_sequence: string
  changing_yao?: number[] | null
  changed_hex_num?: number | null
  changed_hex_name?: string | null
  luck_score: number
  interpretation: string
}

export interface HexagramInfo {
  num: number
  name: string
  symbol: string
  trigram_upper: string
  trigram_lower: string
  meaning: string
  image: string
  judgement: string
  yao_texts: string[]
}

export interface CoinResult {
  sequence: number // 6-9
  type: 'old-yin' | 'young-yang' | 'young-yin' | 'old-yang'
  display: string
}
