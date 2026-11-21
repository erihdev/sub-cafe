#!/usr/bin/env bash
# أدواتُ السمع — تُثبَّتُ عند بدءِ كلِّ جلسةٍ سحابيّة حتى «يسمع» Claude أصواتَ فيديوهاتِ صُب.
# المساحةُ السحابيّةُ مؤقّتة: كلُّ ما يُثبَّتُ فيها يُمسحُ بانتهاءِ الجلسة، فهذا الخطّافُ يُعيدُه تلقائيّاً.
# على جهازِ المطوّرِ لا يَفعلُ شيئاً.
#   بلا وسيط : الأدواتُ الخفيفة (تفريغُ الكلام «ويسبر»، بطاقةُ الصوت، المقارنةُ بالنصّ).
#   full     : يُضيفُ الأدواتِ الثقيلة (الرموزُ الصوتيّة والمحاذاة: torch و transformers) — تُطلَبُ عند الحاجة.
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
MODE="${1:-light}"

# في الخلفيّة: لا تتأخّرُ بدايةُ الجلسة. النماذجُ نفسُها تُنزَّلُ عند أوّلِ استعمال.
(
  python3 -c "import faster_whisper, librosa, parselmouth, soundfile" 2>/dev/null \
    || timeout 600 pip install --quiet --user --break-system-packages faster-whisper librosa praat-parselmouth soundfile
  if [ "$MODE" = "full" ]; then
    python3 -c "import torch, torchaudio, transformers" 2>/dev/null \
      || timeout 900 pip install --quiet --user --break-system-packages torch torchaudio transformers
  fi
  command -v ffmpeg >/dev/null 2>&1 || echo "تنبيه: ffmpeg غير موجود؛ أدواتُ السمع تحتاجُه لفكِّ الملفّات."
  python3 -c "import faster_whisper, librosa, parselmouth, soundfile; print('أدوات السمع جاهزة')"
) > /tmp/ear-setup.log 2>&1 &
disown 2>/dev/null || true
exit 0
