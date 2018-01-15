#Конвертер эмодзи

EMODJI_SET = {
    u':rus:': u'🇷🇺',
    u':uzb:': u'🇺🇿',
    u':set:': u'🛠',
    u':main:': u'📲',
    u':lang:': u'💬',
    u':tv:': u'🖥',
    u':FAQ:': u'❓',
    u':news:': u'🗞',
    u':1:': u'1️⃣',
    u':2:': u'2️⃣',
    u':3:': u'3️⃣',
    u':4:': u'4️⃣',
    u':5:': u'5️⃣',
    u':6:': u'6️⃣',
    u':7:': u'7️⃣',
    u':8:': u'8️⃣',
    u':9:': u'9️⃣',
    u':def:': u'❔',
}

def converter(code):
    if code in EMODJI_SET:
        return EMODJI_SET[code]
    else:
        return code