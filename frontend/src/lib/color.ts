// Continuous interpolation within the single sequential blue hue (see
// palette.md's sequential ramp), for the conditional-probability
// heatmap. This stays within one hue -- never introduces a second color
// -- which is what keeps a magnitude encoding "sequential" rather than
// an accidental rainbow.

function hexToRgb(hex: string): [number, number, number] {
  const clean = hex.replace("#", "")
  const value = parseInt(clean, 16)
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255]
}

function rgbToHex([r, g, b]: [number, number, number]): string {
  const toHex = (n: number) => Math.round(Math.max(0, Math.min(255, n))).toString(16).padStart(2, "0")
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`
}

const SEQ_LIGHT = hexToRgb("#cde2fb") // seq-100
const SEQ_DARK = hexToRgb("#0d366b") // seq-700

/** t in [0, 1] -> a hex color along the sequential blue ramp. */
export function sequentialBlue(t: number): string {
  const clamped = Math.max(0, Math.min(1, t))
  const mixed: [number, number, number] = [
    SEQ_LIGHT[0] + (SEQ_DARK[0] - SEQ_LIGHT[0]) * clamped,
    SEQ_LIGHT[1] + (SEQ_DARK[1] - SEQ_LIGHT[1]) * clamped,
    SEQ_LIGHT[2] + (SEQ_DARK[2] - SEQ_LIGHT[2]) * clamped,
  ]
  return rgbToHex(mixed)
}

/** Text color (black/white ink) that stays legible on a sequentialBlue(t) fill. */
export function textOnSequential(t: number): string {
  return t > 0.55 ? "#ffffff" : "#0b0b0b"
}
