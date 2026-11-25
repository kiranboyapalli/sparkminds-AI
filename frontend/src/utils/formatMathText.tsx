import React from 'react';

/**
 * SparkMinds AI — Student-Friendly Math & Markdown Renderer
 * ---------------------------------------------------------
 * Converts raw LaTeX delimiters ($$...$$, $...$, \[...\], \(...\)), LaTeX macros
 * (\frac, \sqrt, \times, \sin^2, \theta, \pi, \circ, \leq, \geq, etc.), and broken
 * math tokens (such as "cin^2" or orphaned "$") into crisp, readable mathematical
 * typography while strictly preserving:
 *   - Fenced code blocks (``` ... ```)
 *   - Genuine currency prices ($5, $12.50, $1,200, ₹500)
 *   - Multilingual text (Telugu, Hindi, Tamil, Kannada, etc.)
 */

const SUPER_MAP: Record<string, string> = {
  '0': '⁰',
  '1': '¹',
  '2': '²',
  '3': '³',
  '4': '⁴',
  '5': '⁵',
  '6': '⁶',
  '7': '⁷',
  '8': '⁸',
  '9': '⁹',
  '+': '⁺',
  '-': '⁻',
  '=': '⁼',
  '(': '⁽',
  ')': '⁾',
  n: 'ⁿ',
  i: 'ⁱ',
  x: 'ˣ',
  y: 'ʸ',
};

const SUB_MAP: Record<string, string> = {
  '0': '₀',
  '1': '₁',
  '2': '₂',
  '3': '₃',
  '4': '₄',
  '5': '₅',
  '6': '₆',
  '7': '₇',
  '8': '₈',
  '9': '₉',
  '+': '₊',
  '-': '₋',
  '=': '₌',
  '(': '₍',
  ')': '₎',
  a: 'ₐ',
  e: 'ₑ',
  o: 'ₒ',
  x: 'ₓ',
  n: 'ₙ',
};

const LATEX_SYMBOLS: Array<[RegExp, string]> = [
  [/\\Longleftrightarrow/g, '⇔'],
  [/\\Leftrightarrow/g, '⇔'],
  [/\\Longrightarrow/g, '⇒'],
  [/\\Longleftarrow/g, '⇐'],
  [/\\longrightarrow/g, '→'],
  [/\\longleftarrow/g, '←'],
  [/\\Rightarrow/g, '⇒'],
  [/\\Leftarrow/g, '⇐'],
  [/\\rightarrow/g, '→'],
  [/\\leftarrow/g, '←'],
  [/\\leftrightarrow/g, '↔'],
  [/\\implies/g, '⇒'],
  [/\\iff/g, '⇔'],
  [/\\to\b/g, '→'],
  [/\\times\b/g, '×'],
  [/\\cdot\b/g, '·'],
  [/\\div\b/g, '÷'],
  [/\\pm\b/g, '±'],
  [/\\mp\b/g, '∓'],
  [/\\neq\b/g, '≠'],
  [/\\ne\b/g, '≠'],
  [/\\leq\b/g, '≤'],
  [/\\le\b/g, '≤'],
  [/\\geq\b/g, '≥'],
  [/\\ge\b/g, '≥'],
  [/\\approx\b/g, '≈'],
  [/\\equiv\b/g, '≡'],
  [/\\propto\b/g, '∝'],
  [/\\infty\b/g, '∞'],
  [/\\therefore\b/g, '∴'],
  [/\\because\b/g, '∵'],
  [/\\angle\b/g, '∠'],
  [/\\triangle\b/g, '△'],
  [/\\perp\b/g, '⊥'],
  [/\\parallel\b/g, '∥'],
  [/\\cong\b/g, '≅'],
  [/\\degree\b/g, '°'],
  [/\\circ\b/g, '°'],
  [/\\pi\b/g, 'π'],
  [/\\theta\b/g, 'θ'],
  [/\\alpha\b/g, 'α'],
  [/\\beta\b/g, 'β'],
  [/\\gamma\b/g, 'γ'],
  [/\\delta\b/g, 'δ'],
  [/\\Delta\b/g, 'Δ'],
  [/\\lambda\b/g, 'λ'],
  [/\\mu\b/g, 'μ'],
  [/\\sigma\b/g, 'σ'],
  [/\\Sigma\b/g, 'Σ'],
  [/\\omega\b/g, 'ω'],
  [/\\Omega\b/g, 'Ω'],
  [/\\phi\b/g, 'φ'],
  [/\\sum\b/g, '∑'],
  [/\\int\b/g, '∫'],
  [/\\in\b/g, '∈'],
  [/\\notin\b/g, '∉'],
  [/\\subset\b/g, '⊂'],
  [/\\cup\b/g, '∪'],
  [/\\cap\b/g, '∩'],
  [/\\ldots\b/g, '…'],
  [/\\cdots\b/g, '⋯'],
  [/\\quad\b/g, '  '],
  [/\\qquad\b/g, '   '],
  [/\\[,;:!]/g, ' '],
  [/\\(sin|cos|tan|cot|sec|csc|cosec|log|ln|lim|exp|max|min)\b/g, '$1'],
];

function toSup(s: string): string {
  const clean = s.trim();
  if (!clean) return '';
  if (clean === '°' || clean === '\\circ' || clean === 'circ') return '°';
  if ([...clean].every((c) => SUPER_MAP[c])) {
    return [...clean].map((c) => SUPER_MAP[c]).join('');
  }
  return `^(${clean})`;
}

function toSub(s: string): string {
  const clean = s.trim();
  if (!clean) return '';
  if ([...clean].every((c) => SUB_MAP[c])) {
    return [...clean].map((c) => SUB_MAP[c]).join('');
  }
  return `_${clean}`;
}

function extractBraced(str: string, openIdx: number): [string, number] {
  if (openIdx >= str.length || str[openIdx] !== '{') return ['', openIdx];
  let depth = 0;
  let out = '';
  for (let i = openIdx; i < str.length; i++) {
    const ch = str[i];
    if (ch === '{') {
      if (depth > 0) out += ch;
      depth++;
    } else if (ch === '}') {
      depth--;
      if (depth === 0) return [out, i + 1];
      out += ch;
    } else {
      out += ch;
    }
  }
  return [out, str.length];
}

function replaceTextCommands(expr: string): string {
  let out = expr;
  const rx = /\\(?:text|textrm|textbf|textit|mathrm|mathbf|mathit|mathsf|operatorname|boxed)\s*\{/;
  for (let i = 0; i < 8; i++) {
    const m = rx.exec(out);
    if (!m) break;
    const [body, after] = extractBraced(out, m.index + m[0].length - 1);
    out = out.slice(0, m.index) + body + out.slice(after);
  }
  return out;
}

function replaceFracs(expr: string): string {
  let out = expr;
  const rx = /\\[dt]?frac\s*\{/;
  for (let i = 0; i < 6; i++) {
    const m = rx.exec(out);
    if (!m) break;
    const [num, afterNum] = extractBraced(out, m.index + m[0].length - 1);
    let ws = afterNum;
    while (ws < out.length && /\s/.test(out[ws])) ws++;
    let den = '';
    let afterDen = ws;
    if (out[ws] === '{') {
      [den, afterDen] = extractBraced(out, ws);
    } else if (ws < out.length) {
      den = out[ws];
      afterDen = ws + 1;
    }
    const nClean = convertMathBody(num).trim();
    const dClean = convertMathBody(den).trim();
    const simpleN = /^[A-Za-z0-9πθ√²³]+$/.test(nClean);
    const simpleD = /^[A-Za-z0-9πθ√²³]+$/.test(dClean);
    const rep = `${simpleN ? nClean : `(${nClean})`}/${simpleD ? dClean : `(${dClean})`}`;
    out = out.slice(0, m.index) + rep + out.slice(afterDen);
  }
  return out;
}

function replaceSqrts(expr: string): string {
  let out = expr;
  const rx = /\\sqrt(?:\[([^\]]+)\])?\s*\{/;
  for (let i = 0; i < 6; i++) {
    const m = rx.exec(out);
    if (!m) break;
    const deg = (m[1] || '').trim();
    const [body, after] = extractBraced(out, m.index + m[0].length - 1);
    const cleanBody = convertMathBody(body).trim();
    const prefix = deg && deg !== '2' ? `${toSup(deg)}√` : '√';
    const rep = /^[A-Za-z0-9πθ]+$/.test(cleanBody) ? `${prefix}${cleanBody}` : `${prefix}(${cleanBody})`;
    out = out.slice(0, m.index) + rep + out.slice(after);
  }
  return out;
}

export function convertMathBody(raw: string): string {
  if (!raw) return '';
  let out = raw.trim();
  out = out.replace(/\bcin\s*\^/g, 'sin^');
  out = out.replace(/\\(?:left|right|big|Big|bigg|Bigg)\b/g, '');
  out = out.replace(/\\begin\{(?:aligned|align\*?|equation\*?|gather\*?)\}/g, '');
  out = out.replace(/\\end\{(?:aligned|align\*?|equation\*?|gather\*?)\}/g, '');
  out = out.replace(/&=/g, '=').replace(/\\\\/g, '\n');

  out = replaceTextCommands(out);
  out = replaceFracs(out);
  out = replaceSqrts(out);

  for (const [rx, rep] of LATEX_SYMBOLS) {
    out = out.replace(rx, rep);
  }

  out = out.replace(/\^\s*\{?\s*°\s*\}?/g, '°');

  // Braced superscripts ^{...}
  for (let i = 0; i < 8; i++) {
    const m = /\^\s*\{/.exec(out);
    if (!m) break;
    const [body, after] = extractBraced(out, m.index + m[0].length - 1);
    out = out.slice(0, m.index) + toSup(body) + out.slice(after);
  }
  // Braced subscripts _{...}
  for (let i = 0; i < 8; i++) {
    const m = /_\s*\{/.exec(out);
    if (!m) break;
    const [body, after] = extractBraced(out, m.index + m[0].length - 1);
    out = out.slice(0, m.index) + toSub(body) + out.slice(after);
  }

  out = out.replace(/([A-Za-z0-9)θπ°])\^([0-9n])(?![0-9A-Za-z])/g, (_, b, e) => `${b}${toSup(e)}`);
  out = out.replace(/\b([A-Za-z]{1,2})_([0-9]+)\b/g, (_, b, s) => `${b}${toSub(s)}`);
  out = out.replace(/\\\{/g, '{').replace(/\\\}/g, '}').replace(/\\%/g, '%').replace(/\\\$/g, '$');
  out = out.replace(/\\([a-zA-Z]+)/g, '$1');
  return out.replace(/[ \t]{2,}/g, ' ').trim();
}

const DISPLAY_BLOCK_SENTINEL_START = '@@MATHBLOCK_START@@';
const DISPLAY_BLOCK_SENTINEL_END = '@@MATHBLOCK_END@@';

export function cleanMathText(input: string, preserveBlockMarkers = false): string {
  if (!input) return '';
  const codeSegments = input.split('```');
  const cleaned = codeSegments.map((seg, idx) => {
    if (idx % 2 === 1) return seg; // keep code blocks untouched

    let text = seg;
    // Fix broken LLM tokens like "cin^2" or "cin^"
    text = text.replace(/\bcin\s*\^\s*(\d+)?/g, (_, exp) => (exp ? `sin${toSup(exp)}` : 'sin'));
    text = text.replace(/\b(sin|cos|tan|cot|sec|csc)\s*\^\s*(?=\s|$|[,.])/g, '$1');

    // Protect genuine currency ($5, $12.50, $1,200)
    const currencies: string[] = [];
    text = text.replace(/\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?(?![0-9A-Za-z\\^_])/g, (match, offset) => {
      const tail = text.slice(offset + match.length, offset + match.length + 12);
      if (/^\s*(?:\$|\^|\\|\/|×|÷|\+|-|=|\*|x\b|y\b)/.test(tail)) {
        return match;
      }
      const token = `@@CUR${currencies.length}@@`;
      currencies.push(match);
      return token;
    });

    // Display math blocks $$...$$ and \[...\]
    const wrapDisplay = (inner: string) => {
      const formatted = convertMathBody(inner);
      return preserveBlockMarkers
        ? `\n${DISPLAY_BLOCK_SENTINEL_START}${formatted}${DISPLAY_BLOCK_SENTINEL_END}\n`
        : `\n${formatted}\n`;
    };
    text = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, inner) => wrapDisplay(inner));
    text = text.replace(/\\\[([\s\S]+?)\\\]/g, (_, inner) => wrapDisplay(inner));

    // Inline math \(...\) and $...$
    text = text.replace(/\\\((.+?)\\\)/gs, (_, inner) => convertMathBody(inner));
    text = text.replace(/(?<!\\)\$([^$\n]+?)(?<!\\)\$/g, (full, inner) => {
      if (inner.includes('\n\n') || inner.length > 220) return full;
      return convertMathBody(inner);
    });

    // Bare LaTeX outside $ delimiters
    if (text.includes('\\')) {
      text = replaceTextCommands(text);
      text = replaceFracs(text);
      text = replaceSqrts(text);
      for (const [rx, rep] of LATEX_SYMBOLS) {
        text = text.replace(rx, rep);
      }
      text = text.replace(/\\(?:left|right)\b/g, '');
    }

    // Bare superscripts/subscripts in prose
    text = text.replace(/\b(sin|cos|tan|cot|sec|csc)\^([0-9])\b/g, (_, fn, exp) => `${fn}${toSup(exp)}`);
    text = text.replace(/([A-Za-z0-9)θπ])\^\{([0-9+\-n]+)\}/g, (_, b, exp) => `${b}${toSup(exp)}`);
    text = text.replace(/([A-Za-z0-9)θπ])\^([0-9n])(?![0-9A-Za-z])/g, (_, b, exp) => `${b}${toSup(exp)}`);
    text = text.replace(/\b(H|O|C|N|S|Cl|Na|Ca|Fe|Mg|CO|SO|NO|NH|CH)_(\d)/g, (_, el, num) => `${el}${toSub(num)}`);

    // Remove stray orphaned math $ delimiters (stashed real currency is safe)
    text = text.replace(/(?<!\w)\$+(?!\d)/g, '');
    text = text.replace(/\$+(?=\s|$|[,.):;!?])/g, '');

    // Restore genuine currency values
    currencies.forEach((val, i) => {
      text = text.split(`@@CUR${i}@@`).join(val);
    });

    return text;
  });
  return cleaned.join('```');
}

const renderInlineRich = (text: string, keyBase: string): React.ReactNode[] => {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|\*[^*\n]+\*)/g);
  return parts.map((p, i) => {
    if (p.startsWith('**') && p.endsWith('**') && p.length > 4) {
      return (
        <strong key={`${keyBase}-${i}`} className="font-extrabold text-[#101B35]">
          {p.slice(2, -2)}
        </strong>
      );
    }
    if (p.startsWith('`') && p.endsWith('`') && p.length > 2) {
      return (
        <code
          key={`${keyBase}-${i}`}
          className="px-1.5 py-0.5 rounded-md bg-[#EEEAFE] text-[#5146E5] font-mono text-[0.86em] font-semibold"
        >
          {p.slice(1, -1)}
        </code>
      );
    }
    if (p.startsWith('*') && p.endsWith('*') && p.length > 2 && !p.startsWith('**')) {
      return (
        <em key={`${keyBase}-${i}`} className="italic text-[#172554]">
          {p.slice(1, -1)}
        </em>
      );
    }
    return <React.Fragment key={`${keyBase}-${i}`}>{p}</React.Fragment>;
  });
};

export const RichMathMarkdown: React.FC<{
  text: string;
  className?: string;
}> = ({ text, className = '' }) => {
  const normalized = React.useMemo(() => cleanMathText(text || '', true), [text]);
  const segments = normalized.split(/```/);

  return (
    <div className={`space-y-2 text-sm leading-relaxed text-[#202943] ${className}`}>
      {segments.map((seg, idx) => {
        if (idx % 2 === 1) {
          const code = seg.replace(/^[a-zA-Z0-9_+-]*\n/, '');
          return (
            <pre
              key={idx}
              className="p-3.5 rounded-xl bg-[#101B35] text-[#35D6E8] text-xs font-mono overflow-x-auto whitespace-pre border border-[#5146E5]/30 shadow-inner"
            >
              {code.trimEnd()}
            </pre>
          );
        }

        // Split display math blocks cleanly
        const lines = seg.split('\n');
        return lines.map((rawLine, li) => {
          const k = `${idx}-${li}`;
          const trimmed = rawLine.trim();
          if (!trimmed) return <div key={k} className="h-1" />;

          if (
            trimmed.startsWith(DISPLAY_BLOCK_SENTINEL_START) &&
            trimmed.endsWith(DISPLAY_BLOCK_SENTINEL_END)
          ) {
            const formula = trimmed
              .slice(DISPLAY_BLOCK_SENTINEL_START.length, -DISPLAY_BLOCK_SENTINEL_END.length)
              .trim();
            return (
              <div key={k} className="spark-math-block">
                {formula}
              </div>
            );
          }

          const cleanLine = trimmed
            .replace(DISPLAY_BLOCK_SENTINEL_START, '')
            .replace(DISPLAY_BLOCK_SENTINEL_END, '');

          // Highlight standalone clean equation lines (e.g., "sin²θ + cos²θ = 1" or "a² + b² = c²")
          const isStandaloneEquation =
            cleanLine.length <= 72 &&
            cleanLine.includes('=') &&
            /[²³⁴⁵⁶⁷⁸⁹√πθ÷×±≤≥≠]|\/\d|\bsin|\bcos|\btan/.test(cleanLine) &&
            !/^[-*•\d#>]|^\*\*/.test(cleanLine) &&
            cleanLine.split(' ').length <= 10;
          if (isStandaloneEquation) {
            return (
              <div key={k} className="spark-math-block">
                {cleanLine}
              </div>
            );
          }

          if (cleanLine === '---' || cleanLine === '***') {
            return <hr key={k} className="border-[#DFE5F6] my-2" />;
          }

          const heading = cleanLine.match(/^#{1,4}\s+(.*)$/);
          if (heading) {
            return (
              <div key={k} className="font-display font-bold text-[#101B35] pt-1.5 text-[0.98rem]">
                {renderInlineRich(heading[1], k)}
              </div>
            );
          }

          const quote = cleanLine.match(/^>\s+(.*)$/);
          if (quote) {
            return (
              <div
                key={k}
                className="pl-3.5 py-1.5 border-l-3 border-[#5146E5] bg-[#F7F9FF] rounded-r-xl text-[#172554] font-medium"
              >
                {renderInlineRich(quote[1], k)}
              </div>
            );
          }

          const bullet = cleanLine.match(/^[-*•]\s+(.*)$/);
          if (bullet) {
            return (
              <div key={k} className="flex gap-2.5 pl-1">
                <span className="text-[#5146E5] font-extrabold shrink-0">•</span>
                <span className="min-w-0">{renderInlineRich(bullet[1], k)}</span>
              </div>
            );
          }

          const numbered = cleanLine.match(/^(\d+)[.)]\s+(.*)$/);
          if (numbered) {
            return (
              <div key={k} className="flex gap-2.5 pl-1">
                <span className="inline-flex items-center justify-center w-5 h-5 rounded-md bg-[#EEEAFE] text-[#5146E5] text-[11px] font-extrabold shrink-0 mt-0.5">
                  {numbered[1]}
                </span>
                <span className="min-w-0">{renderInlineRich(numbered[2], k)}</span>
              </div>
            );
          }

          return (
            <p key={k} className="leading-relaxed">
              {renderInlineRich(cleanLine, k)}
            </p>
          );
        });
      })}
    </div>
  );
};
