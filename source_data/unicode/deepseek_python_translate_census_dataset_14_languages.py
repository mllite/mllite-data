import pandas as pd
import zipfile
import os, csv

# ============================================================
# 1. LOAD THE DATASET
# ============================================================

url = "../../data/raw/census_raw.csv"
columns = [
    'age', 'workclass', 'fnlwgt', 'education', 'education-num',
    'marital-status', 'occupation', 'relationship', 'race', 'sex',
    'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income'
]

df = pd.read_csv(url, skipinitialspace=True)
df.columns = columns
# ============================================================
# 2. WORKCLASS TRANSLATIONS (all 14 languages)
# ============================================================

workclass_maps = {
    'chinese': {
        'Private': '私营企业', 'Self-emp-not-inc': '自营职业（非公司制）',
        'Self-emp-inc': '自营职业（公司制）', 'Federal-gov': '联邦政府',
        'Local-gov': '地方政府', 'State-gov': '州政府',
        'Without-pay': '无薪工作', 'Never-worked': '从未工作过'
    },
    'arabic': {
        'Private': 'قطاع خاص', 'Self-emp-not-inc': 'عمل حر (غير مؤسسي)',
        'Self-emp-inc': 'عمل حر (مؤسسي)', 'Federal-gov': 'حكومة اتحادية',
        'Local-gov': 'حكومة محلية', 'State-gov': 'حكومة ولاية',
        'Without-pay': 'بدون أجر', 'Never-worked': 'لم يعمل مطلقاً'
    },
    'hindi': {
        'Private': 'निजी क्षेत्र', 'Self-emp-not-inc': 'स्वरोज़गार (गैर-निगमित)',
        'Self-emp-inc': 'स्वरोज़गार (निगमित)', 'Federal-gov': 'संघीय सरकार',
        'Local-gov': 'स्थानीय सरकार', 'State-gov': 'राज्य सरकार',
        'Without-pay': 'बिना वेतन', 'Never-worked': 'कभी काम नहीं किया'
    },
    'russian': {
        'Private': 'Частный сектор', 'Self-emp-not-inc': 'Самозанятый (не корпорация)',
        'Self-emp-inc': 'Самозанятый (корпорация)', 'Federal-gov': 'Федеральное правительство',
        'Local-gov': 'Местное правительство', 'State-gov': 'Правительство штата',
        'Without-pay': 'Без оплаты', 'Never-worked': 'Никогда не работал'
    },
    'greek': {
        'Private': 'Ιδιωτικός τομέας', 'Self-emp-not-inc': 'Αυτοαπασχολούμενος (μη εταιρικός)',
        'Self-emp-inc': 'Αυτοαπασχολούμενος (εταιρικός)', 'Federal-gov': 'Ομοσπονδιακή κυβέρνηση',
        'Local-gov': 'Τοπική αυτοδιοίκηση', 'State-gov': 'Κυβέρνηση πολιτείας',
        'Without-pay': 'Χωρίς αμοιβή', 'Never-worked': 'Ποτέ δεν εργάστηκε'
    },
    'portuguese': {
        'Private': 'Setor privado', 'Self-emp-not-inc': 'Autônomo (não incorporado)',
        'Self-emp-inc': 'Autônomo (incorporado)', 'Federal-gov': 'Governo federal',
        'Local-gov': 'Governo local', 'State-gov': 'Governo estadual',
        'Without-pay': 'Sem remuneração', 'Never-worked': 'Nunca trabalhou'
    },
    'amharic': {
        'Private': 'የግል ዘርፍ', 'Self-emp-not-inc': 'ራስን የሚያስተዳድር (ኩባንያ ያልሆነ)',
        'Self-emp-inc': 'ራስን የሚያስተዳድር (ኩባንያ)', 'Federal-gov': 'ፌዴራል መንግሥት',
        'Local-gov': 'የአካባቢ መንግሥት', 'State-gov': 'የክልል መንግሥት',
        'Without-pay': 'ያለ ደሞዝ', 'Never-worked': 'መቼም አልሰራም'
    },
    'spanish': {
        'Private': 'Sector privado', 'Self-emp-not-inc': 'Autónomo (no incorporado)',
        'Self-emp-inc': 'Autónomo (incorporado)', 'Federal-gov': 'Gobierno federal',
        'Local-gov': 'Gobierno local', 'State-gov': 'Gobierno estatal',
        'Without-pay': 'Sin remuneración', 'Never-worked': 'Nunca trabajó'
    },
    'french': {
        'Private': 'Secteur privé', 'Self-emp-not-inc': 'Indépendant (non constitué)',
        'Self-emp-inc': 'Indépendant (constitué)', 'Federal-gov': 'Gouvernement fédéral',
        'Local-gov': 'Gouvernement local', 'State-gov': 'Gouvernement d\'État',
        'Without-pay': 'Sans rémunération', 'Never-worked': 'N\'a jamais travaillé'
    },
    'japanese': {
        'Private': '民間', 'Self-emp-not-inc': '自営業（法人化なし）',
        'Self-emp-inc': '自営業（法人化）', 'Federal-gov': '連邦政府',
        'Local-gov': '地方政府', 'State-gov': '州政府',
        'Without-pay': '無給', 'Never-worked': '就業経験なし'
    },
    'korean': {
        'Private': '민간 부문', 'Self-emp-not-inc': '자영업 (비법인)',
        'Self-emp-inc': '자영업 (법인)', 'Federal-gov': '연방 정부',
        'Local-gov': '지방 정부', 'State-gov': '주 정부',
        'Without-pay': '무급', 'Never-worked': '근무 경험 없음'
    },
    'turkish': {
        'Private': 'Özel sektör', 'Self-emp-not-inc': 'Serbest meslek (şirket değil)',
        'Self-emp-inc': 'Serbest meslek (şirket)', 'Federal-gov': 'Federal hükümet',
        'Local-gov': 'Yerel yönetim', 'State-gov': 'Eyalet hükümeti',
        'Without-pay': 'Ücretsiz', 'Never-worked': 'Hiç çalışmadı'
    },
    'urdu': {
        'Private': 'پرائیویٹ سیکٹر', 'Self-emp-not-inc': 'خود روزگار (غیر کارپوریٹ)',
        'Self-emp-inc': 'خود روزگار (کارپوریٹ)', 'Federal-gov': 'وفاقی حکومت',
        'Local-gov': 'مقامی حکومت', 'State-gov': 'ریاستی حکومت',
        'Without-pay': 'بلا معاوضہ', 'Never-worked': 'کبھی کام نہیں کیا'
    },
    'swahili': {
        'Private': 'Sekta binafsi', 'Self-emp-not-inc': 'Kujiajiri (siyo kampuni)',
        'Self-emp-inc': 'Kujiajiri (kampuni)', 'Federal-gov': 'Serikali ya shirikisho',
        'Local-gov': 'Serikali ya mtaa', 'State-gov': 'Serikali ya jimbo',
        'Without-pay': 'Bila malipo', 'Never-worked': 'Hajawahi kufanya kazi'
    }
}

# ============================================================
# 3. EDUCATION TRANSLATIONS (all 14 languages)
# ============================================================

education_maps = {
    'chinese': {
        'Bachelors': '学士', 'Some-college': '大学肄业', '11th': '十一年级',
        'HS-grad': '高中毕业', 'Prof-school': '专业学院', 'Assoc-acdm': '副学士（学术）',
        'Assoc-voc': '副学士（职业）', '9th': '九年级', '7th-8th': '七至八年级',
        '12th': '十二年级', 'Masters': '硕士', '1st-4th': '一至四年级',
        '10th': '十年级', 'Doctorate': '博士', '5th-6th': '五至六年级',
        'Preschool': '学前班'
    },
    'arabic': {
        'Bachelors': 'بكالوريوس', 'Some-college': 'بعض الكلية (غير مكتمل)',
        '11th': 'الصف الحادي عشر', 'HS-grad': 'ثانوية عامة',
        'Prof-school': 'كلية مهنية', 'Assoc-acdm': 'دبلوم جامعي (أكاديمي)',
        'Assoc-voc': 'دبلوم جامعي (مهني)', '9th': 'الصف التاسع',
        '7th-8th': 'الصف السابع-الثامن', '12th': 'الصف الثاني عشر',
        'Masters': 'ماجستير', '1st-4th': 'الصف الأول-الرابع',
        '10th': 'الصف العاشر', 'Doctorate': 'دكتوراه',
        '5th-6th': 'الصف الخامس-السادس', 'Preschool': 'رياض أطفال'
    },
    'hindi': {
        'Bachelors': 'स्नातक', 'Some-college': 'कुछ कॉलेज (अधूरा)',
        '11th': 'ग्यारहवीं कक्षा', 'HS-grad': 'हाई स्कूल स्नातक',
        'Prof-school': 'व्यावसायिक कॉलेज', 'Assoc-acdm': 'एसोसिएट डिग्री (शैक्षणिक)',
        'Assoc-voc': 'एसोसिएट डिग्री (व्यावसायिक)', '9th': 'नौवीं कक्षा',
        '7th-8th': 'सातवीं-आठवीं कक्षा', '12th': 'बारहवीं कक्षा',
        'Masters': 'मास्टर्स', '1st-4th': 'पहली-चौथी कक्षा',
        '10th': 'दसवीं कक्षा', 'Doctorate': 'डॉक्टरेट',
        '5th-6th': 'पाँचवीं-छठी कक्षा', 'Preschool': 'प्री-स्कूल'
    },
    'russian': {
        'Bachelors': 'Бакалавр', 'Some-college': 'Незаконченное высшее',
        '11th': '11-й класс', 'HS-grad': 'Среднее образование',
        'Prof-school': 'Профессиональное училище', 'Assoc-acdm': 'Младший специалист (академический)',
        'Assoc-voc': 'Младший специалист (профессиональный)', '9th': '9-й класс',
        '7th-8th': '7-8-й класс', '12th': '12-й класс',
        'Masters': 'Магистр', '1st-4th': '1-4-й класс',
        '10th': '10-й класс', 'Doctorate': 'Доктор наук',
        '5th-6th': '5-6-й класс', 'Preschool': 'Детский сад'
    },
    'greek': {
        'Bachelors': 'Πτυχίο', 'Some-college': 'Μερική φοίτηση σε κολέγιο',
        '11th': '11η τάξη', 'HS-grad': 'Απόφοιτος λυκείου',
        'Prof-school': 'Επαγγελματική σχολή', 'Assoc-acdm': 'Προπτυχιακό δίπλωμα (ακαδημαϊκό)',
        'Assoc-voc': 'Προπτυχιακό δίπλωμα (επαγγελματικό)', '9th': '9η τάξη',
        '7th-8th': '7η-8η τάξη', '12th': '12η τάξη',
        'Masters': 'Μεταπτυχιακό', '1st-4th': '1η-4η τάξη',
        '10th': '10η τάξη', 'Doctorate': 'Διδακτορικό',
        '5th-6th': '5η-6η τάξη', 'Preschool': 'Προσχολική αγωγή'
    },
    'portuguese': {
        'Bachelors': 'Bacharelado', 'Some-college': 'Faculdade incompleta',
        '11th': '11º ano', 'HS-grad': 'Ensino médio completo',
        'Prof-school': 'Escola profissionalizante', 'Assoc-acdm': 'Curso superior (acadêmico)',
        'Assoc-voc': 'Curso superior (profissionalizante)', '9th': '9º ano',
        '7th-8th': '7º-8º ano', '12th': '12º ano',
        'Masters': 'Mestrado', '1st-4th': '1º-4º ano',
        '10th': '10º ano', 'Doctorate': 'Doutorado',
        '5th-6th': '5º-6º ano', 'Preschool': 'Pré-escola'
    },
    'amharic': {
        'Bachelors': 'የመጀመሪያ ዲግሪ', 'Some-college': 'የኮሌጅ ትምህርት (ያልተጠናቀቀ)',
        '11th': '11ኛ ክፍል', 'HS-grad': 'ሁለተኛ ደረጃ ትምህርት ያጠናቀቀ',
        'Prof-school': 'የሙያ ትምህርት ቤት', 'Assoc-acdm': 'ዲፕሎማ (አካዳሚክ)',
        'Assoc-voc': 'ዲፕሎማ (ሙያዊ)', '9th': '9ኛ ክፍል',
        '7th-8th': '7-8ኛ ክፍል', '12th': '12ኛ ክፍል',
        'Masters': 'ማስተርስ', '1st-4th': '1-4ኛ ክፍል',
        '10th': '10ኛ ክፍል', 'Doctorate': 'ዶክትሬት',
        '5th-6th': '5-6ኛ ክፍል', 'Preschool': 'ቅድመ መደበኛ ትምህርት'
    },
    'spanish': {
        'Bachelors': 'Licenciatura', 'Some-college': 'Universidad incompleta',
        '11th': '11º grado', 'HS-grad': 'Bachillerato completo',
        'Prof-school': 'Escuela profesional', 'Assoc-acdm': 'Técnico superior (académico)',
        'Assoc-voc': 'Técnico superior (profesional)', '9th': '9º grado',
        '7th-8th': '7º-8º grado', '12th': '12º grado',
        'Masters': 'Maestría', '1st-4th': '1º-4º grado',
        '10th': '10º grado', 'Doctorate': 'Doctorado',
        '5th-6th': '5º-6º grado', 'Preschool': 'Preescolar'
    },
    'french': {
        'Bachelors': 'Licence', 'Some-college': 'Université incomplète',
        '11th': '11e année', 'HS-grad': 'Lycée diplômé',
        'Prof-school': 'École professionnelle', 'Assoc-acdm': 'Diplôme universitaire (académique)',
        'Assoc-voc': 'Diplôme universitaire (professionnel)', '9th': '9e année',
        '7th-8th': '7e-8e année', '12th': '12e année',
        'Masters': 'Master', '1st-4th': '1re-4e année',
        '10th': '10e année', 'Doctorate': 'Doctorat',
        '5th-6th': '5e-6e année', 'Preschool': 'École maternelle'
    },
    'japanese': {
        'Bachelors': '学士', 'Some-college': '大学中退',
        '11th': '高校1年', 'HS-grad': '高校卒業',
        'Prof-school': '専門学校', 'Assoc-acdm': '短期大学士（学術）',
        'Assoc-voc': '短期大学士（職業）', '9th': '中学3年',
        '7th-8th': '中学1-2年', '12th': '高校3年',
        'Masters': '修士', '1st-4th': '小学1-4年',
        '10th': '高校2年', 'Doctorate': '博士',
        '5th-6th': '小学5-6年', 'Preschool': '幼稚園'
    },
    'korean': {
        'Bachelors': '학사', 'Some-college': '대학교 중퇴',
        '11th': '고등학교 1학년', 'HS-grad': '고등학교 졸업',
        'Prof-school': '전문 학교', 'Assoc-acdm': '전문학사 (학술)',
        'Assoc-voc': '전문학사 (직업)', '9th': '중학교 3학년',
        '7th-8th': '중학교 1-2학년', '12th': '고등학교 3학년',
        'Masters': '석사', '1st-4th': '초등학교 1-4학년',
        '10th': '고등학교 2학년', 'Doctorate': '박사',
        '5th-6th': '초등학교 5-6학년', 'Preschool': '유치원'
    },
    'turkish': {
        'Bachelors': 'Lisans', 'Some-college': 'Üniversite terk',
        '11th': '11. sınıf', 'HS-grad': 'Lise mezunu',
        'Prof-school': 'Meslek okulu', 'Assoc-acdm': 'Ön lisans (akademik)',
        'Assoc-voc': 'Ön lisans (mesleki)', '9th': '9. sınıf',
        '7th-8th': '7-8. sınıf', '12th': '12. sınıf',
        'Masters': 'Yüksek lisans', '1st-4th': '1-4. sınıf',
        '10th': '10. sınıf', 'Doctorate': 'Doktora',
        '5th-6th': '5-6. sınıf', 'Preschool': 'Anaokulu'
    },
    'urdu': {
        'Bachelors': 'بیچلر', 'Some-college': 'کچھ کالج (نامکمل)',
        '11th': 'گیارہویں جماعت', 'HS-grad': 'ہائی اسکول مکمل',
        'Prof-school': 'پیشہ ورانہ کالج', 'Assoc-acdm': 'ایسوسی ایٹ ڈگری (تعلیمی)',
        'Assoc-voc': 'ایسوسی ایٹ ڈگری (پیشہ ورانہ)', '9th': 'نویں جماعت',
        '7th-8th': 'ساتویں-آٹھویں جماعت', '12th': 'بارہویں جماعت',
        'Masters': 'ماسٹرز', '1st-4th': 'پہلی-چوتھی جماعت',
        '10th': 'دسویں جماعت', 'Doctorate': 'ڈاکٹریٹ',
        '5th-6th': 'پانچویں-چھٹی جماعت', 'Preschool': 'پری اسکول'
    },
    'swahili': {
        'Bachelors': 'Shahada ya kwanza', 'Some-college': 'Chuo kikuu kisichokamilika',
        '11th': 'Darasa la 11', 'HS-grad': 'Shule ya sekondari imekamilika',
        'Prof-school': 'Shule ya ufundi', 'Assoc-acdm': 'Diploma (kielimu)',
        'Assoc-voc': 'Diploma (kiufundi)', '9th': 'Darasa la 9',
        '7th-8th': 'Darasa la 7-8', '12th': 'Darasa la 12',
        'Masters': 'Shahada ya uzamili', '1st-4th': 'Darasa la 1-4',
        '10th': 'Darasa la 10', 'Doctorate': 'Shahada ya udaktari',
        '5th-6th': 'Darasa la 5-6', 'Preschool': 'Shule ya awali'
    }
}

# ============================================================
# 4. MARITAL STATUS TRANSLATIONS (all 14 languages)
# ============================================================

marital_maps = {
    'chinese': {
        'Married-civ-spouse': '已婚（民事配偶）', 'Divorced': '离异',
        'Never-married': '未婚', 'Separated': '分居',
        'Widowed': '丧偶', 'Married-spouse-absent': '已婚（配偶不在）',
        'Married-AF-spouse': '已婚（军人配偶）'
    },
    'arabic': {
        'Married-civ-spouse': 'متزوج (زوج/زوجة مدني)', 'Divorced': 'مطلق',
        'Never-married': 'لم يتزوج مطلقاً', 'Separated': 'منفصل',
        'Widowed': 'أرمل', 'Married-spouse-absent': 'متزوج (الزوج/الزوجة غائب)',
        'Married-AF-spouse': 'متزوج (زوج/زوجة عسكري)'
    },
    'hindi': {
        'Married-civ-spouse': 'विवाहित (नागरिक पति/पत्नी)', 'Divorced': 'तलाकशुदा',
        'Never-married': 'अविवाहित', 'Separated': 'अलग रहने वाला',
        'Widowed': 'विधुर/विधवा', 'Married-spouse-absent': 'विवाहित (पति/पत्नी अनुपस्थित)',
        'Married-AF-spouse': 'विवाहित (सैन्य पति/पत्नी)'
    },
    'russian': {
        'Married-civ-spouse': 'Женат/замужем (гражданский брак)', 'Divorced': 'Разведён/разведена',
        'Never-married': 'Никогда не был(а) в браке', 'Separated': 'В разлуке',
        'Widowed': 'Вдовец/вдова', 'Married-spouse-absent': 'Женат/замужем (супруг/супруга отсутствует)',
        'Married-AF-spouse': 'Женат/замужем (военный супруг/супруга)'
    },
    'greek': {
        'Married-civ-spouse': 'Παντρεμένος/η (πολιτικός γάμος)', 'Divorced': 'Διαζευγμένος/η',
        'Never-married': 'Ποτέ παντρεμένος/η', 'Separated': 'Σε διάσταση',
        'Widowed': 'Χήρος/χήρα', 'Married-spouse-absent': 'Παντρεμένος/η (σύζυγος απών/ούσα)',
        'Married-AF-spouse': 'Παντρεμένος/η (στρατιωτικός σύζυγος)'
    },
    'portuguese': {
        'Married-civ-spouse': 'Casado(a) (casamento civil)', 'Divorced': 'Divorciado(a)',
        'Never-married': 'Nunca casado(a)', 'Separated': 'Separado(a)',
        'Widowed': 'Viúvo(a)', 'Married-spouse-absent': 'Casado(a) (cônjuge ausente)',
        'Married-AF-spouse': 'Casado(a) (cônjuge militar)'
    },
    'amharic': {
        'Married-civ-spouse': 'ያገባ/ያገባች (ሲቪል ጋብቻ)', 'Divorced': 'የተፋታ/የተፋታች',
        'Never-married': 'ጋብቻ ያልፈጸመ/ያልፈጸመች', 'Separated': 'ተለያይቷል/ተለያይታለች',
        'Widowed': 'ባል/ሚስት የሞተባት/የሞተበት', 'Married-spouse-absent': 'ያገባ/ያገባች (ባል/ሚስት የሌለ)',
        'Married-AF-spouse': 'ያገባ/ያገባች (ወታደራዊ ባል/ሚስት)'
    },
    'spanish': {
        'Married-civ-spouse': 'Casado(a) (matrimonio civil)', 'Divorced': 'Divorciado(a)',
        'Never-married': 'Nunca casado(a)', 'Separated': 'Separado(a)',
        'Widowed': 'Viudo(a)', 'Married-spouse-absent': 'Casado(a) (cónyuge ausente)',
        'Married-AF-spouse': 'Casado(a) (cónyuge militar)'
    },
    'french': {
        'Married-civ-spouse': 'Marié(e) (mariage civil)', 'Divorced': 'Divorcé(e)',
        'Never-married': 'Jamais marié(e)', 'Separated': 'Séparé(e)',
        'Widowed': 'Veuf/veuve', 'Married-spouse-absent': 'Marié(e) (conjoint absent)',
        'Married-AF-spouse': 'Marié(e) (conjoint militaire)'
    },
    'japanese': {
        'Married-civ-spouse': '既婚（民事婚）', 'Divorced': '離婚',
        'Never-married': '未婚', 'Separated': '別居',
        'Widowed': '死別', 'Married-spouse-absent': '既婚（配偶者不在）',
        'Married-AF-spouse': '既婚（軍人配偶者）'
    },
    'korean': {
        'Married-civ-spouse': '기혼 (민간 결혼)', 'Divorced': '이혼',
        'Never-married': '미혼', 'Separated': '별거',
        'Widowed': '사별', 'Married-spouse-absent': '기혼 (배우자 부재)',
        'Married-AF-spouse': '기혼 (군인 배우자)'
    },
    'turkish': {
        'Married-civ-spouse': 'Evli (medeni nikah)', 'Divorced': 'Boşanmış',
        'Never-married': 'Hiç evlenmemiş', 'Separated': 'Ayrı',
        'Widowed': 'Dul', 'Married-spouse-absent': 'Evli (eş yok)',
        'Married-AF-spouse': 'Evli (asker eş)'
    },
    'urdu': {
        'Married-civ-spouse': 'شادی شدہ (سول شادی)', 'Divorced': 'طلاق یافتہ',
        'Never-married': 'غیر شادی شدہ', 'Separated': 'علیحدہ',
        'Widowed': 'بیوہ/بیوہ', 'Married-spouse-absent': 'شادی شدہ (شریک حیات غیر حاضر)',
        'Married-AF-spouse': 'شادی شدہ (فوجی شریک حیات)'
    },
    'swahili': {
        'Married-civ-spouse': 'Ndoa (ndoa ya kiraia)', 'Divorced': 'Talaka',
        'Never-married': 'Haijawahi kuoa/kuolewa', 'Separated': 'Kutengana',
        'Widowed': 'Mjane', 'Married-spouse-absent': 'Ndoa (mwenzi hayupo)',
        'Married-AF-spouse': 'Ndoa (mwenzi wa kijeshi)'
    }
}

# ============================================================
# 5. OCCUPATION TRANSLATIONS (all 14 languages)
# ============================================================

occupation_maps = {
    'chinese': {
        'Tech-support': '技术支持', 'Craft-repair': '手工艺/维修',
        'Other-service': '其他服务业', 'Sales': '销售',
        'Exec-managerial': '高管/管理', 'Prof-specialty': '专业技术',
        'Handlers-cleaners': '搬运/清洁', 'Machine-op-inspct': '机械操作/质检',
        'Adm-clerical': '行政/文职', 'Farming-fishing': '农业/渔业',
        'Transport-moving': '运输/搬运', 'Priv-house-serv': '私人家庭服务',
        'Protective-serv': '安保服务', 'Armed-Forces': '武装部队'
    },
    'arabic': {
        'Tech-support': 'دعم تقني', 'Craft-repair': 'حرفي/صيانة',
        'Other-service': 'خدمات أخرى', 'Sales': 'مبيعات',
        'Exec-managerial': 'تنفيذي/إداري', 'Prof-specialty': 'متخصص مهني',
        'Handlers-cleaners': 'عامل مناولة/تنظيف', 'Machine-op-inspct': 'تشغيل آلات/تفتيش',
        'Adm-clerical': 'إداري/كتابي', 'Farming-fishing': 'زراعة/صيد',
        'Transport-moving': 'نقل/شحن', 'Priv-house-serv': 'خدمة منزلية خاصة',
        'Protective-serv': 'خدمات أمنية', 'Armed-Forces': 'قوات مسلحة'
    },
    'hindi': {
        'Tech-support': 'तकनीकी सहायता', 'Craft-repair': 'शिल्प/मरम्मत',
        'Other-service': 'अन्य सेवाएँ', 'Sales': 'बिक्री',
        'Exec-managerial': 'कार्यकारी/प्रबंधकीय', 'Prof-specialty': 'व्यावसायिक विशेषज्ञ',
        'Handlers-cleaners': 'हैंडलर/सफाई कर्मचारी', 'Machine-op-inspct': 'मशीन ऑपरेटर/निरीक्षक',
        'Adm-clerical': 'प्रशासनिक/लेखाकारी', 'Farming-fishing': 'कृषि/मछली पालन',
        'Transport-moving': 'परिवहन/ढुलाई', 'Priv-house-serv': 'निजी घरेलू सेवा',
        'Protective-serv': 'सुरक्षा सेवाएँ', 'Armed-Forces': 'सशस्त्र बल'
    },
    'russian': {
        'Tech-support': 'Техническая поддержка', 'Craft-repair': 'Ремесло/ремонт',
        'Other-service': 'Другие услуги', 'Sales': 'Продажи',
        'Exec-managerial': 'Руководитель/менеджер', 'Prof-specialty': 'Профессиональный специалист',
        'Handlers-cleaners': 'Разнорабочий/уборщик', 'Machine-op-inspct': 'Оператор станков/инспектор',
        'Adm-clerical': 'Административный/офисный работник', 'Farming-fishing': 'Сельское хозяйство/рыболовство',
        'Transport-moving': 'Транспорт/перевозки', 'Priv-house-serv': 'Домашняя прислуга',
        'Protective-serv': 'Охранные службы', 'Armed-Forces': 'Вооружённые силы'
    },
    'greek': {
        'Tech-support': 'Τεχνική υποστήριξη', 'Craft-repair': 'Τεχνίτης/επισκευές',
        'Other-service': 'Άλλες υπηρεσίες', 'Sales': 'Πωλήσεις',
        'Exec-managerial': 'Στέλεχος/διευθυντικό στέλεχος', 'Prof-specialty': 'Επαγγελματίας ειδικός',
        'Handlers-cleaners': 'Εργάτης/καθαριστής', 'Machine-op-inspct': 'Χειριστής μηχανημάτων/επιθεωρητής',
        'Adm-clerical': 'Διοικητικός/γραφειακός υπάλληλος', 'Farming-fishing': 'Γεωργία/αλιεία',
        'Transport-moving': 'Μεταφορές/μετακόμιση', 'Priv-house-serv': 'Οικιακό προσωπικό',
        'Protective-serv': 'Υπηρεσίες ασφαλείας', 'Armed-Forces': 'Ένοπλες δυνάμεις'
    },
    'portuguese': {
        'Tech-support': 'Suporte técnico', 'Craft-repair': 'Artesão/repair',
        'Other-service': 'Outros serviços', 'Sales': 'Vendas',
        'Exec-managerial': 'Executivo/gerencial', 'Prof-specialty': 'Especialista profissional',
        'Handlers-cleaners': 'Operador/limpeza', 'Machine-op-inspct': 'Operador de máquinas/inspeção',
        'Adm-clerical': 'Administrativo/escriturário', 'Farming-fishing': 'Agricultura/pesca',
        'Transport-moving': 'Transporte/mudanças', 'Priv-house-serv': 'Serviço doméstico particular',
        'Protective-serv': 'Serviços de segurança', 'Armed-Forces': 'Forças armadas'
    },
    'amharic': {
        'Tech-support': 'ቴክኒካዊ ድጋፍ', 'Craft-repair': 'የእጅ ጥበብ/ጥገና',
        'Other-service': 'ሌሎች አገልግሎቶች', 'Sales': 'ሽያጭ',
        'Exec-managerial': 'አስፈፃሚ/አስተዳዳሪ', 'Prof-specialty': 'ባለሙያ ስፔሻሊስት',
        'Handlers-cleaners': 'ተቆጣጣሪ/አጽጃ', 'Machine-op-inspct': 'ማሽን ኦፕሬተር/መርማሪ',
        'Adm-clerical': 'አስተዳደራዊ/ፅህፈት', 'Farming-fishing': 'እርሻ/ዓሣ ማጥመድ',
        'Transport-moving': 'መጓጓዣ/ማጓጓዝ', 'Priv-house-serv': 'የግል የቤት አገልግሎት',
        'Protective-serv': 'የጥበቃ አገልግሎቶች', 'Armed-Forces': 'ታጥቀው ኃይሎች'
    },
    'spanish': {
        'Tech-support': 'Soporte técnico', 'Craft-repair': 'Artesano/reparaciones',
        'Other-service': 'Otros servicios', 'Sales': 'Ventas',
        'Exec-managerial': 'Ejecutivo/gerencial', 'Prof-specialty': 'Especialista profesional',
        'Handlers-cleaners': 'Manipulador/limpieza', 'Machine-op-inspct': 'Operador de máquinas/inspección',
        'Adm-clerical': 'Administrativo/oficinista', 'Farming-fishing': 'Agricultura/pesca',
        'Transport-moving': 'Transporte/mudanzas', 'Priv-house-serv': 'Servicio doméstico privado',
        'Protective-serv': 'Servicios de seguridad', 'Armed-Forces': 'Fuerzas armadas'
    },
    'french': {
        'Tech-support': 'Support technique', 'Craft-repair': 'Artisan/réparation',
        'Other-service': 'Autres services', 'Sales': 'Ventes',
        'Exec-managerial': 'Cadre/direction', 'Prof-specialty': 'Spécialiste professionnel',
        'Handlers-cleaners': 'Manutention/nettoyage', 'Machine-op-inspct': 'Opérateur de machines/inspection',
        'Adm-clerical': 'Administratif/bureau', 'Farming-fishing': 'Agriculture/pêche',
        'Transport-moving': 'Transport/déménagement', 'Priv-house-serv': 'Service domestique privé',
        'Protective-serv': 'Services de sécurité', 'Armed-Forces': 'Forces armées'
    },
    'japanese': {
        'Tech-support': 'テクニカルサポート', 'Craft-repair': '職人/修理',
        'Other-service': 'その他のサービス', 'Sales': '営業',
        'Exec-managerial': '経営幹部/管理職', 'Prof-specialty': '専門職',
        'Handlers-cleaners': '運搬/清掃', 'Machine-op-inspct': '機械操作/検査',
        'Adm-clerical': '事務/管理', 'Farming-fishing': '農業/漁業',
        'Transport-moving': '輸送/運搬', 'Priv-house-serv': '個人宅サービス',
        'Protective-serv': '警備サービス', 'Armed-Forces': '軍隊'
    },
    'korean': {
        'Tech-support': '기술 지원', 'Craft-repair': '기술/수리',
        'Other-service': '기타 서비스', 'Sales': '영업',
        'Exec-managerial': '임원/관리직', 'Prof-specialty': '전문직',
        'Handlers-cleaners': '운반/청소', 'Machine-op-inspct': '기계 조작/검사',
        'Adm-clerical': '사무/관리', 'Farming-fishing': '농업/어업',
        'Transport-moving': '운송/이동', 'Priv-house-serv': '개인 가사 서비스',
        'Protective-serv': '보안 서비스', 'Armed-Forces': '군대'
    },
    'turkish': {
        'Tech-support': 'Teknik destek', 'Craft-repair': 'Zanaat/onarım',
        'Other-service': 'Diğer hizmetler', 'Sales': 'Satış',
        'Exec-managerial': 'Yönetici/idari', 'Prof-specialty': 'Uzman',
        'Handlers-cleaners': 'Taşıma/temizlik', 'Machine-op-inspct': 'Makine operatörü/muayene',
        'Adm-clerical': 'İdari/büro', 'Farming-fishing': 'Tarım/balıkçılık',
        'Transport-moving': 'Taşıma/nakliye', 'Priv-house-serv': 'Özel ev hizmeti',
        'Protective-serv': 'Güvenlik hizmetleri', 'Armed-Forces': 'Silahlı kuvvetler'
    },
    'urdu': {
        'Tech-support': 'تکنیکی معاونت', 'Craft-repair': 'دستکاری/مرمت',
        'Other-service': 'دیگر خدمات', 'Sales': 'فروخت',
        'Exec-managerial': 'ایگزیکٹو/مینیجری', 'Prof-specialty': 'پیشہ ور ماہر',
        'Handlers-cleaners': 'ہینڈلر/صفائی', 'Machine-op-inspct': 'مشین آپریٹر/معائنہ',
        'Adm-clerical': 'انتظامی/کلریکل', 'Farming-fishing': 'زراعت/ماہی گیری',
        'Transport-moving': 'ٹرانسپورٹ/منتقلی', 'Priv-house-serv': 'نجی گھریلو خدمت',
        'Protective-serv': 'حفاظتی خدمات', 'Armed-Forces': 'مسلح افواج'
    },
    'swahili': {
        'Tech-support': 'Msaada wa kiufundi', 'Craft-repair': 'Ufundi/matengenezo',
        'Other-service': 'Huduma nyingine', 'Sales': 'Mauzo',
        'Exec-managerial': 'Mtendaji/kiutawala', 'Prof-specialty': 'Mtaalamu',
        'Handlers-cleaners': 'Mshughulikiaji/usafi', 'Machine-op-inspct': 'Opereta wa mashine/ukaguzi',
        'Adm-clerical': 'Kiutawala/karani', 'Farming-fishing': 'Kilimo/uvuvi',
        'Transport-moving': 'Usafirishaji/hamisho', 'Priv-house-serv': 'Huduma ya nyumbani binafsi',
        'Protective-serv': 'Huduma za ulinzi', 'Armed-Forces': 'Jeshi'
    }
}

# ============================================================
# 6. RELATIONSHIP TRANSLATIONS (all 14 languages)
# ============================================================

relationship_maps = {
    'chinese': {
        'Wife': '妻子', 'Own-child': '子女', 'Husband': '丈夫',
        'Not-in-family': '非家庭成员', 'Other-relative': '其他亲属',
        'Unmarried': '未婚伴侣'
    },
    'arabic': {
        'Wife': 'زوجة', 'Own-child': 'ابن/ابنة', 'Husband': 'زوج',
        'Not-in-family': 'ليس من العائلة', 'Other-relative': 'قريب آخر',
        'Unmarried': 'شريك غير متزوج'
    },
    'hindi': {
        'Wife': 'पत्नी', 'Own-child': 'अपनी संतान', 'Husband': 'पति',
        'Not-in-family': 'परिवार से बाहर', 'Other-relative': 'अन्य रिश्तेदार',
        'Unmarried': 'अविवाहित साथी'
    },
    'russian': {
        'Wife': 'Жена', 'Own-child': 'Ребёнок', 'Husband': 'Муж',
        'Not-in-family': 'Не член семьи', 'Other-relative': 'Другой родственник',
        'Unmarried': 'Не состоящий в браке партнёр'
    },
    'greek': {
        'Wife': 'Σύζυγος (γυναίκα)', 'Own-child': 'Παιδί', 'Husband': 'Σύζυγος (άνδρας)',
        'Not-in-family': 'Δεν ανήκει στην οικογένεια', 'Other-relative': 'Άλλος συγγενής',
        'Unmarried': 'Ανύπαντρος/η σύντροφος'
    },
    'portuguese': {
        'Wife': 'Esposa', 'Own-child': 'Filho(a)', 'Husband': 'Marido',
        'Not-in-family': 'Não é da família', 'Other-relative': 'Outro parente',
        'Unmarried': 'Companheiro(a) não casado(a)'
    },
    'amharic': {
        'Wife': 'ሚስት', 'Own-child': 'የራስ ልጅ', 'Husband': 'ባል',
        'Not-in-family': 'ከቤተሰብ ውጭ', 'Other-relative': 'ሌላ ዘመድ',
        'Unmarried': 'ያላገባ/ያላገባች አጋር'
    },
    'spanish': {
        'Wife': 'Esposa', 'Own-child': 'Hijo(a)', 'Husband': 'Esposo',
        'Not-in-family': 'No es de la familia', 'Other-relative': 'Otro pariente',
        'Unmarried': 'Pareja no casada'
    },
    'french': {
        'Wife': 'Épouse', 'Own-child': 'Enfant', 'Husband': 'Mari',
        'Not-in-family': 'Pas de la famille', 'Other-relative': 'Autre parent',
        'Unmarried': 'Partenaire non marié'
    },
    'japanese': {
        'Wife': '妻', 'Own-child': '子', 'Husband': '夫',
        'Not-in-family': '家族外', 'Other-relative': '他の親族',
        'Unmarried': '未婚パートナー'
    },
    'korean': {
        'Wife': '아내', 'Own-child': '자녀', 'Husband': '남편',
        'Not-in-family': '가족 아님', 'Other-relative': '다른 친척',
        'Unmarried': '미혼 파트너'
    },
    'turkish': {
        'Wife': 'Eş (kadın)', 'Own-child': 'Çocuk', 'Husband': 'Eş (erkek)',
        'Not-in-family': 'Aileden değil', 'Other-relative': 'Diğer akraba',
        'Unmarried': 'Evli olmayan partner'
    },
    'urdu': {
        'Wife': 'بیوی', 'Own-child': 'اپنی اولاد', 'Husband': 'شوہر',
        'Not-in-family': 'خاندان سے باہر', 'Other-relative': 'دوسرے رشتہ دار',
        'Unmarried': 'غیر شادی شدہ ساتھی'
    },
    'swahili': {
        'Wife': 'Mke', 'Own-child': 'Mtoto', 'Husband': 'Mume',
        'Not-in-family': 'Si wa familia', 'Other-relative': 'Ndugu mwingine',
        'Unmarried': 'Mwenzi ambaye hajaoa/kuolewa'
    }
}

# ============================================================
# 7. RACE TRANSLATIONS (all 14 languages)
# ============================================================

race_maps = {
    'chinese': {'White': '白人', 'Asian-Pac-Islander': '亚裔/太平洋岛民',
                'Amer-Indian-Eskimo': '美洲原住民/因纽特人', 'Other': '其他', 'Black': '黑人'},
    'arabic': {'White': 'أبيض', 'Asian-Pac-Islander': 'آسيوي/جزر المحيط الهادئ',
               'Amer-Indian-Eskimo': 'أمريكي أصلي/إسكيمو', 'Other': 'أخرى', 'Black': 'أسود'},
    'hindi': {'White': 'श्वेत', 'Asian-Pac-Islander': 'एशियाई/प्रशांत द्वीपवासी',
              'Amer-Indian-Eskimo': 'मूल अमेरिकी/एस्किमो', 'Other': 'अन्य', 'Black': 'अश्वेत'},
    'russian': {'White': 'Белый', 'Asian-Pac-Islander': 'Азиат/житель Тихоокеанских островов',
                'Amer-Indian-Eskimo': 'Коренной американец/эскимос', 'Other': 'Другая', 'Black': 'Чёрный'},
    'greek': {'White': 'Λευκός/η', 'Asian-Pac-Islander': 'Ασιάτης/κάτοικος νήσων Ειρηνικού',
              'Amer-Indian-Eskimo': 'Ιθαγενής Αμερικής/Εσκιμώος', 'Other': 'Άλλο', 'Black': 'Μαύρος/η'},
    'portuguese': {'White': 'Branco(a)', 'Asian-Pac-Islander': 'Asiático/ilhas do Pacífico',
                   'Amer-Indian-Eskimo': 'Nativo americano/esquimó', 'Other': 'Outro', 'Black': 'Negro(a)'},
    'amharic': {'White': 'ነጭ', 'Asian-Pac-Islander': 'እስያዊ/ፓሲፊክ ደሴት ነዋሪ',
                'Amer-Indian-Eskimo': 'አሜሪካዊ ተወላጅ/እስኪሞ', 'Other': 'ሌላ', 'Black': 'ጥቁር'},
    'spanish': {'White': 'Blanco(a)', 'Asian-Pac-Islander': 'Asiático/islas del Pacífico',
                'Amer-Indian-Eskimo': 'Nativo americano/esquimal', 'Other': 'Otro', 'Black': 'Negro(a)'},
    'french': {'White': 'Blanc(he)', 'Asian-Pac-Islander': 'Asiatique/îles du Pacifique',
               'Amer-Indian-Eskimo': 'Amérindien/Esquimau', 'Other': 'Autre', 'Black': 'Noir(e)'},
    'japanese': {'White': '白人', 'Asian-Pac-Islander': 'アジア系/太平洋諸島系',
                 'Amer-Indian-Eskimo': 'ネイティブアメリカン/エスキモー', 'Other': 'その他', 'Black': '黒人'},
    'korean': {'White': '백인', 'Asian-Pac-Islander': '아시아/태평양 제도인',
               'Amer-Indian-Eskimo': '아메리카 원주민/에스키모', 'Other': '기타', 'Black': '흑인'},
    'turkish': {'White': 'Beyaz', 'Asian-Pac-Islander': 'Asyalı/Pasifik Adalı',
                'Amer-Indian-Eskimo': 'Kızılderili/Eskimo', 'Other': 'Diğer', 'Black': 'Siyah'},
    'urdu': {'White': 'سفید', 'Asian-Pac-Islander': 'ایشیائی/بحر الکاہل جزیرے',
             'Amer-Indian-Eskimo': 'مقامی امریکی/ایسکیمو', 'Other': 'دیگر', 'Black': 'سیاہ'},
    'swahili': {'White': 'Mweupe', 'Asian-Pac-Islander': 'Mwasia/visiwa vya Pasifiki',
                'Amer-Indian-Eskimo': 'Mwamerindi/Eskimo', 'Other': 'Nyingine', 'Black': 'Mweusi'}
}

# ============================================================
# 8. SEX TRANSLATIONS (all 14 languages)
# ============================================================

sex_maps = {
    'chinese': {'Male': '男', 'Female': '女'},
    'arabic': {'Male': 'ذكر', 'Female': 'أنثى'},
    'hindi': {'Male': 'पुरुष', 'Female': 'महिला'},
    'russian': {'Male': 'Мужской', 'Female': 'Женский'},
    'greek': {'Male': 'Άνδρας', 'Female': 'Γυναίκα'},
    'portuguese': {'Male': 'Masculino', 'Female': 'Feminino'},
    'amharic': {'Male': 'ወንድ', 'Female': 'ሴት'},
    'spanish': {'Male': 'Masculino', 'Female': 'Femenino'},
    'french': {'Male': 'Masculin', 'Female': 'Féminin'},
    'japanese': {'Male': '男性', 'Female': '女性'},
    'korean': {'Male': '남성', 'Female': '여성'},
    'turkish': {'Male': 'Erkek', 'Female': 'Kadın'},
    'urdu': {'Male': 'مرد', 'Female': 'خاتون'},
    'swahili': {'Male': 'Mwanamume', 'Female': 'Mwanamke'}
}

# ============================================================
# 9. INCOME TRANSLATIONS (all 14 languages)
# ============================================================

income_maps = {
    'chinese': {'<=50K': '低于或等于5万美元', '>50K': '高于5万美元'},
    'arabic': {'<=50K': 'أقل من أو يساوي 50 ألف دولار', '>50K': 'أكثر من 50 ألف دولار'},
    'hindi': {'<=50K': '50 हज़ार डॉलर से कम या बराबर', '>50K': '50 हज़ार डॉलर से अधिक'},
    'russian': {'<=50K': 'Менее или равно 50 тыс. долларов', '>50K': 'Более 50 тыс. долларов'},
    'greek': {'<=50K': 'Λιγότερο ή ίσο με 50.000 δολάρια', '>50K': 'Πάνω από 50.000 δολάρια'},
    'portuguese': {'<=50K': 'Menos ou igual a 50 mil dólares', '>50K': 'Mais de 50 mil dólares'},
    'amharic': {'<=50K': 'ከ50 ሺህ ዶላር በታች ወይም እኩል', '>50K': 'ከ50 ሺህ ዶላር በላይ'},
    'spanish': {'<=50K': 'Menos o igual a 50 mil dólares', '>50K': 'Más de 50 mil dólares'},
    'french': {'<=50K': 'Moins ou égal à 50 000 dollars', '>50K': 'Plus de 50 000 dollars'},
    'japanese': {'<=50K': '5万ドル以下', '>50K': '5万ドル超'},
    'korean': {'<=50K': '5만 달러 이하', '>50K': '5만 달러 초과'},
    'turkish': {'<=50K': '50 bin dolardan az veya eşit', '>50K': '50 bin dolardan fazla'},
    'urdu': {'<=50K': '50 ہزار ڈالر سے کم یا برابر', '>50K': '50 ہزار ڈالر سے زیادہ'},
    'swahili': {'<=50K': 'Chini au sawa na dola 50,000', '>50K': 'Zaidi ya dola 50,000'}
}

# ============================================================
# 10. HEADER TRANSLATIONS (all 14 languages)
# ============================================================

# CONTINUED IN PART 2...# ============================================================
# 10. HEADER TRANSLATIONS (all 14 languages) - CONTINUED
# ============================================================

header_maps = {
    'chinese': {
        'age': '年龄', 'workclass': '工作类型', 'fnlwgt': '人口权重系数',
        'education': '教育程度', 'education-num': '受教育年限',
        'marital-status': '婚姻状况', 'occupation': '职业',
        'relationship': '家庭关系', 'race': '种族', 'sex': '性别',
        'capital-gain': '资本收益', 'capital-loss': '资本损失',
        'hours-per-week': '每周工作时长', 'native-country': '原籍国',
        'income': '收入'
    },
    'arabic': {
        'age': 'العمر', 'workclass': 'نوع العمل', 'fnlwgt': 'معامل الوزن السكاني',
        'education': 'المستوى التعليمي', 'education-num': 'سنوات التعليم',
        'marital-status': 'الحالة الاجتماعية', 'occupation': 'المهنة',
        'relationship': 'العلاقة الأسرية', 'race': 'العرق', 'sex': 'الجنس',
        'capital-gain': 'أرباح رأس المال', 'capital-loss': 'خسائر رأس المال',
        'hours-per-week': 'ساعات العمل الأسبوعية', 'native-country': 'البلد الأصلي',
        'income': 'الدخل'
    },
    'hindi': {
        'age': 'आयु', 'workclass': 'कार्य वर्ग', 'fnlwgt': 'जनसंख्या भार गुणांक',
        'education': 'शैक्षिक स्तर', 'education-num': 'शिक्षा के वर्ष',
        'marital-status': 'वैवाहिक स्थिति', 'occupation': 'व्यवसाय',
        'relationship': 'पारिवारिक संबंध', 'race': 'नस्ल', 'sex': 'लिंग',
        'capital-gain': 'पूंजीगत लाभ', 'capital-loss': 'पूंजीगत हानि',
        'hours-per-week': 'साप्ताहिक कार्य घंटे', 'native-country': 'मूल देश',
        'income': 'आय'
    },
    'russian': {
        'age': 'Возраст', 'workclass': 'Категория занятости', 'fnlwgt': 'Весовой коэффициент населения',
        'education': 'Уровень образования', 'education-num': 'Лет образования',
        'marital-status': 'Семейное положение', 'occupation': 'Профессия',
        'relationship': 'Семейные отношения', 'race': 'Раса', 'sex': 'Пол',
        'capital-gain': 'Прирост капитала', 'capital-loss': 'Потеря капитала',
        'hours-per-week': 'Часов работы в неделю', 'native-country': 'Страна происхождения',
        'income': 'Доход'
    },
    'greek': {
        'age': 'Ηλικία', 'workclass': 'Κατηγορία εργασίας', 'fnlwgt': 'Συντελεστής βάρους πληθυσμού',
        'education': 'Εκπαιδευτικό επίπεδο', 'education-num': 'Έτη εκπαίδευσης',
        'marital-status': 'Οικογενειακή κατάσταση', 'occupation': 'Επάγγελμα',
        'relationship': 'Οικογενειακή σχέση', 'race': 'Φυλή', 'sex': 'Φύλο',
        'capital-gain': 'Κεφαλαιακό κέρδος', 'capital-loss': 'Κεφαλαιακή ζημία',
        'hours-per-week': 'Ώρες εργασίας ανά εβδομάδα', 'native-country': 'Χώρα καταγωγής',
        'income': 'Εισόδημα'
    },
    'portuguese': {
        'age': 'Idade', 'workclass': 'Categoria de trabalho', 'fnlwgt': 'Peso populacional',
        'education': 'Nível educacional', 'education-num': 'Anos de educação',
        'marital-status': 'Estado civil', 'occupation': 'Ocupação',
        'relationship': 'Relação familiar', 'race': 'Raça', 'sex': 'Sexo',
        'capital-gain': 'Ganho de capital', 'capital-loss': 'Perda de capital',
        'hours-per-week': 'Horas por semana', 'native-country': 'País de origem',
        'income': 'Renda'
    },
    'amharic': {
        'age': 'ዕድሜ', 'workclass': 'የሥራ ዓይነት', 'fnlwgt': 'የህዝብ ክብደት ቅንጅት',
        'education': 'የትምህርት ደረጃ', 'education-num': 'የትምህርት ዓመታት',
        'marital-status': 'የጋብቻ ሁኔታ', 'occupation': 'ሙያ',
        'relationship': 'የቤተሰብ ግንኙነት', 'race': 'ዘር', 'sex': 'ጾታ',
        'capital-gain': 'የካፒታል ትርፍ', 'capital-loss': 'የካፒታል ኪሳራ',
        'hours-per-week': 'በሳምንት የሚሰሩት ሰዓታት', 'native-country': 'የትውልድ አገር',
        'income': 'ገቢ'
    },
    'spanish': {
        'age': 'Edad', 'workclass': 'Tipo de trabajo', 'fnlwgt': 'Coeficiente de ponderación',
        'education': 'Nivel educativo', 'education-num': 'Años de educación',
        'marital-status': 'Estado civil', 'occupation': 'Ocupación',
        'relationship': 'Relación familiar', 'race': 'Raza', 'sex': 'Sexo',
        'capital-gain': 'Ganancia de capital', 'capital-loss': 'Pérdida de capital',
        'hours-per-week': 'Horas semanales', 'native-country': 'País de origen',
        'income': 'Ingreso'
    },
    'french': {
        'age': 'Âge', 'workclass': 'Catégorie d\'emploi', 'fnlwgt': 'Coefficient de pondération',
        'education': 'Niveau d\'éducation', 'education-num': 'Années d\'études',
        'marital-status': 'Situation matrimoniale', 'occupation': 'Profession',
        'relationship': 'Lien familial', 'race': 'Race', 'sex': 'Sexe',
        'capital-gain': 'Gain en capital', 'capital-loss': 'Perte en capital',
        'hours-per-week': 'Heures par semaine', 'native-country': 'Pays d\'origine',
        'income': 'Revenu'
    },
    'japanese': {
        'age': '年齢', 'workclass': '雇用区分', 'fnlwgt': '人口ウェイト',
        'education': '教育レベル', 'education-num': '教育年数',
        'marital-status': '婚姻状況', 'occupation': '職業',
        'relationship': '家族関係', 'race': '人種', 'sex': '性別',
        'capital-gain': 'キャピタルゲイン', 'capital-loss': 'キャピタルロス',
        'hours-per-week': '週間労働時間', 'native-country': '出身国',
        'income': '収入'
    },
    'korean': {
        'age': '나이', 'workclass': '고용 유형', 'fnlwgt': '인구 가중치',
        'education': '교육 수준', 'education-num': '교육 연수',
        'marital-status': '결혼 상태', 'occupation': '직업',
        'relationship': '가족 관계', 'race': '인종', 'sex': '성별',
        'capital-gain': '자본 이득', 'capital-loss': '자본 손실',
        'hours-per-week': '주당 근무 시간', 'native-country': '출신 국가',
        'income': '소득'
    },
    'turkish': {
        'age': 'Yaş', 'workclass': 'Çalışma kategorisi', 'fnlwgt': 'Nüfus ağırlığı',
        'education': 'Eğitim düzeyi', 'education-num': 'Eğitim yılı',
        'marital-status': 'Medeni durum', 'occupation': 'Meslek',
        'relationship': 'Aile ilişkisi', 'race': 'Irk', 'sex': 'Cinsiyet',
        'capital-gain': 'Sermaye kazancı', 'capital-loss': 'Sermaye kaybı',
        'hours-per-week': 'Haftalık çalışma saati', 'native-country': 'Doğum ülkesi',
        'income': 'Gelir'
    },
    'urdu': {
        'age': 'عمر', 'workclass': 'ملازمت کی قسم', 'fnlwgt': 'آبادی کا وزنی عدد',
        'education': 'تعلیمی سطح', 'education-num': 'تعلیم کے سال',
        'marital-status': 'ازدواجی حیثیت', 'occupation': 'پیشہ',
        'relationship': 'خاندانی تعلق', 'race': 'نسل', 'sex': 'جنس',
        'capital-gain': 'سرمایہ کاری کا فائدہ', 'capital-loss': 'سرمایہ کاری کا نقصان',
        'hours-per-week': 'ہفتہ وار کام کے اوقات', 'native-country': 'ملک پیدائش',
        'income': 'آمدنی'
    },
    'swahili': {
        'age': 'Umri', 'workclass': 'Aina ya kazi', 'fnlwgt': 'Uzito wa idadi ya watu',
        'education': 'Kiwango cha elimu', 'education-num': 'Miaka ya elimu',
        'marital-status': 'Hali ya ndoa', 'occupation': 'Kazi',
        'relationship': 'Uhusiano wa kifamilia', 'race': 'Rangi', 'sex': 'Jinsia',
        'capital-gain': 'Faida ya mtaji', 'capital-loss': 'Hasara ya mtaji',
        'hours-per-week': 'Saa za kazi kwa wiki', 'native-country': 'Nchi asili',
        'income': 'Mapato'
    }
}

# ============================================================
# 11. COUNTRY TRANSLATIONS (all 14 languages)
# ============================================================

# ============================================================
# COUNTRY TRANSLATIONS (all 14 languages)
# ============================================================

country_translations = {
    # ===== 1. CHINESE (中文) =====
    'chinese': {
        'United-States': '美国', 'Mexico': '墨西哥', 'Philippines': '菲律宾',
        'Germany': '德国', 'Canada': '加拿大', 'Puerto-Rico': '波多黎各',
        'El-Salvador': '萨尔瓦多', 'India': '印度', 'United-Kingdom': '英国',
        'Japan': '日本', 'Italy': '意大利', 'Poland': '波兰', 'China': '中国',
        'Cuba': '古巴', 'Haiti': '海地', 'Dominican-Republic': '多米尼加共和国',
        'Nicaragua': '尼加拉瓜', 'Honduras': '洪都拉斯', 'Guatemala': '危地马拉',
        'France': '法国', 'Taiwan': '台湾', 'Jamaica': '牙买加',
        'Trinidad&Tobago': '特立尼达和多巴哥', 'Ecuador': '厄瓜多尔',
        'Peru': '秘鲁', 'South': '南斯拉夫', 'Portugal': '葡萄牙',
        'Ireland': '爱尔兰', 'Greece': '希腊', 'Hungary': '匈牙利',
        'Iran': '伊朗', 'Columbia': '哥伦比亚', 'Cambodia': '柬埔寨',
        'Thailand': '泰国', 'Laos': '老挝', 'Vietnam': '越南',
        'Hong': '香港', 'Yugoslavia': '南斯拉夫',
        'Outlying-US(Guam-USVI-etc)': '美国海外领地',
        'Scotland': '苏格兰', 'England': '英格兰', 'Holand-Netherlands': '荷兰'
    },
    
    # ===== 2. ARABIC (العربية) =====
    'arabic': {
        'United-States': 'الولايات المتحدة', 'Mexico': 'المكسيك',
        'Philippines': 'الفلبين', 'Germany': 'ألمانيا', 'Canada': 'كندا',
        'Puerto-Rico': 'بورتوريكو', 'El-Salvador': 'السلفادور',
        'India': 'الهند', 'United-Kingdom': 'المملكة المتحدة',
        'Japan': 'اليابان', 'Italy': 'إيطاليا', 'Poland': 'بولندا',
        'China': 'الصين', 'Cuba': 'كوبا', 'Haiti': 'هايتي',
        'Dominican-Republic': 'جمهورية الدومينيكان',
        'Nicaragua': 'نيكاراغوا', 'Honduras': 'هندوراس',
        'Guatemala': 'غواتيمالا', 'France': 'فرنسا',
        'Taiwan': 'تايوان', 'Jamaica': 'جامايكا',
        'Trinidad&Tobago': 'ترينيداد وتوباغو', 'Ecuador': 'الإكوادور',
        'Peru': 'بيرو', 'South': 'جنوب', 'Portugal': 'البرتغال',
        'Ireland': 'أيرلندا', 'Greece': 'اليونان', 'Hungary': 'المجر',
        'Iran': 'إيران', 'Columbia': 'كولومبيا', 'Cambodia': 'كمبوديا',
        'Thailand': 'تايلاند', 'Laos': 'لاوس', 'Vietnam': 'فيتنام',
        'Hong': 'هونغ كونغ', 'Yugoslavia': 'يوغوسلافيا',
        'Outlying-US(Guam-USVI-etc)': 'أقاليم الولايات المتحدة الخارجية',
        'Scotland': 'اسكتلندا', 'England': 'إنجلترا',
        'Holand-Netherlands': 'هولندا'
    },
    
    # ===== 3. HINDI (हिन्दी) =====
    'hindi': {
        'United-States': 'संयुक्त राज्य अमेरिका', 'Mexico': 'मेक्सिको',
        'Philippines': 'फिलीपींस', 'Germany': 'जर्मनी',
        'Canada': 'कनाडा', 'Puerto-Rico': 'प्यूर्टो रिको',
        'El-Salvador': 'अल साल्वाडोर', 'India': 'भारत',
        'United-Kingdom': 'यूनाइटेड किंगडम', 'Japan': 'जापान',
        'Italy': 'इटली', 'Poland': 'पोलैंड', 'China': 'चीन',
        'Cuba': 'क्यूबा', 'Haiti': 'हैती',
        'Dominican-Republic': 'डोमिनिकन गणराज्य',
        'Nicaragua': 'निकारागुआ', 'Honduras': 'होंडुरास',
        'Guatemala': 'ग्वाटेमाला', 'France': 'फ्रांस',
        'Taiwan': 'ताइवान', 'Jamaica': 'जमैका',
        'Trinidad&Tobago': 'त्रिनिदाद और टोबैगो',
        'Ecuador': 'इक्वाडोर', 'Peru': 'पेरू',
        'South': 'दक्षिण', 'Portugal': 'पुर्तगाल',
        'Ireland': 'आयरलैंड', 'Greece': 'ग्रीस',
        'Hungary': 'हंगरी', 'Iran': 'ईरान',
        'Columbia': 'कोलंबिया', 'Cambodia': 'कंबोडिया',
        'Thailand': 'थाईलैंड', 'Laos': 'लाओस',
        'Vietnam': 'वियतनाम', 'Hong': 'हांगकांग',
        'Yugoslavia': 'यूगोस्लाविया',
        'Outlying-US(Guam-USVI-etc)': 'अमेरिकी बाहरी क्षेत्र',
        'Scotland': 'स्कॉटलैंड', 'England': 'इंग्लैंड',
        'Holand-Netherlands': 'नीदरलैंड'
    },
    
    # ===== 4. RUSSIAN (Русский) =====
    'russian': {
        'United-States': 'Соединённые Штаты', 'Mexico': 'Мексика',
        'Philippines': 'Филиппины', 'Germany': 'Германия',
        'Canada': 'Канада', 'Puerto-Rico': 'Пуэрто-Рико',
        'El-Salvador': 'Сальвадор', 'India': 'Индия',
        'United-Kingdom': 'Великобритания', 'Japan': 'Япония',
        'Italy': 'Италия', 'Poland': 'Польша', 'China': 'Китай',
        'Cuba': 'Куба', 'Haiti': 'Гаити',
        'Dominican-Republic': 'Доминиканская Республика',
        'Nicaragua': 'Никарагуа', 'Honduras': 'Гондурас',
        'Guatemala': 'Гватемала', 'France': 'Франция',
        'Taiwan': 'Тайвань', 'Jamaica': 'Ямайка',
        'Trinidad&Tobago': 'Тринидад и Тобаго',
        'Ecuador': 'Эквадор', 'Peru': 'Перу',
        'South': 'Юг', 'Portugal': 'Португалия',
        'Ireland': 'Ирландия', 'Greece': 'Греция',
        'Hungary': 'Венгрия', 'Iran': 'Иран',
        'Columbia': 'Колумбия', 'Cambodia': 'Камбоджа',
        'Thailand': 'Таиланд', 'Laos': 'Лаос',
        'Vietnam': 'Вьетнам', 'Hong': 'Гонконг',
        'Yugoslavia': 'Югославия',
        'Outlying-US(Guam-USVI-etc)': 'Внешние территории США',
        'Scotland': 'Шотландия', 'England': 'Англия',
        'Holand-Netherlands': 'Нидерланды'
    },
    
    # ===== 5. GREEK (Ελληνικά) =====
    'greek': {
        'United-States': 'Ηνωμένες Πολιτείες', 'Mexico': 'Μεξικό',
        'Philippines': 'Φιλιππίνες', 'Germany': 'Γερμανία',
        'Canada': 'Καναδάς', 'Puerto-Rico': 'Πουέρτο Ρίκο',
        'El-Salvador': 'Ελ Σαλβαδόρ', 'India': 'Ινδία',
        'United-Kingdom': 'Ηνωμένο Βασίλειο', 'Japan': 'Ιαπωνία',
        'Italy': 'Ιταλία', 'Poland': 'Πολωνία', 'China': 'Κίνα',
        'Cuba': 'Κούβα', 'Haiti': 'Αϊτή',
        'Dominican-Republic': 'Δομινικανή Δημοκρατία',
        'Nicaragua': 'Νικαράγουα', 'Honduras': 'Ονδούρα',
        'Guatemala': 'Γουατεμάλα', 'France': 'Γαλλία',
        'Taiwan': 'Ταϊβάν', 'Jamaica': 'Τζαμάικα',
        'Trinidad&Tobago': 'Τρινιντάντ και Τομπάγκο',
        'Ecuador': 'Εκουαδόρ', 'Peru': 'Περού',
        'South': 'Νότος', 'Portugal': 'Πορτογαλία',
        'Ireland': 'Ιρλανδία', 'Greece': 'Ελλάδα',
        'Hungary': 'Ουγγαρία', 'Iran': 'Ιράν',
        'Columbia': 'Κολομβία', 'Cambodia': 'Καμπότζη',
        'Thailand': 'Ταϊλάνδη', 'Laos': 'Λάος',
        'Vietnam': 'Βιετνάμ', 'Hong': 'Χονγκ Κονγκ',
        'Yugoslavia': 'Γιουγκοσλαβία',
        'Outlying-US(Guam-USVI-etc)': 'Υπερπόντιες κτήσεις ΗΠΑ',
        'Scotland': 'Σκωτία', 'England': 'Αγγλία',
        'Holand-Netherlands': 'Ολλανδία'
    },
    
    # ===== 6. PORTUGUESE (Português) =====
    'portuguese': {
        'United-States': 'Estados Unidos', 'Mexico': 'México',
        'Philippines': 'Filipinas', 'Germany': 'Alemanha',
        'Canada': 'Canadá', 'Puerto-Rico': 'Porto Rico',
        'El-Salvador': 'El Salvador', 'India': 'Índia',
        'United-Kingdom': 'Reino Unido', 'Japan': 'Japão',
        'Italy': 'Itália', 'Poland': 'Polônia', 'China': 'China',
        'Cuba': 'Cuba', 'Haiti': 'Haiti',
        'Dominican-Republic': 'República Dominicana',
        'Nicaragua': 'Nicarágua', 'Honduras': 'Honduras',
        'Guatemala': 'Guatemala', 'France': 'França',
        'Taiwan': 'Taiwan', 'Jamaica': 'Jamaica',
        'Trinidad&Tobago': 'Trinidad e Tobago',
        'Ecuador': 'Equador', 'Peru': 'Peru',
        'South': 'Sul', 'Portugal': 'Portugal',
        'Ireland': 'Irlanda', 'Greece': 'Grécia',
        'Hungary': 'Hungria', 'Iran': 'Irã',
        'Columbia': 'Colômbia', 'Cambodia': 'Camboja',
        'Thailand': 'Tailândia', 'Laos': 'Laos',
        'Vietnam': 'Vietnã', 'Hong': 'Hong Kong',
        'Yugoslavia': 'Iugoslávia',
        'Outlying-US(Guam-USVI-etc)': 'Territórios americanos',
        'Scotland': 'Escócia', 'England': 'Inglaterra',
        'Holand-Netherlands': 'Holanda'
    },
    
    # ===== 7. AMHARIC (አማርኛ) =====
    'amharic': {
        'United-States': 'አሜሪካ', 'Mexico': 'ሜክሲኮ',
        'Philippines': 'ፊሊፒንስ', 'Germany': 'ጀርመን',
        'Canada': 'ካናዳ', 'Puerto-Rico': 'ፑርቶ ሪኮ',
        'El-Salvador': 'ኤል ሳልቫዶር', 'India': 'ህንድ',
        'United-Kingdom': 'ዩናይትድ ኪንግደም', 'Japan': 'ጃፓን',
        'Italy': 'ጣሊያን', 'Poland': 'ፖላንድ', 'China': 'ቻይና',
        'Cuba': 'ኩባ', 'Haiti': 'ሃይቲ',
        'Dominican-Republic': 'ዶሚኒካን ሪፐብሊክ',
        'Nicaragua': 'ኒካራጓ', 'Honduras': 'ሆንዱራስ',
        'Guatemala': 'ጓቲማላ', 'France': 'ፈረንሳይ',
        'Taiwan': 'ታይዋን', 'Jamaica': 'ጃማይካ',
        'Trinidad&Tobago': 'ትሪኒዳድ እና ቶባጎ',
        'Ecuador': 'ኢኳዶር', 'Peru': 'ፔሩ',
        'South': 'ደቡብ', 'Portugal': 'ፖርቱጋል',
        'Ireland': 'አየርላንድ', 'Greece': 'ግሪክ',
        'Hungary': 'ሀንጋሪ', 'Iran': 'ኢራን',
        'Columbia': 'ኮሎምቢያ', 'Cambodia': 'ካምቦዲያ',
        'Thailand': 'ታይላንድ', 'Laos': 'ላኦስ',
        'Vietnam': 'ቬትናም', 'Hong': 'ሆንግ ኮንግ',
        'Yugoslavia': 'ዩጎስላቪያ',
        'Outlying-US(Guam-USVI-etc)': 'የአሜሪካ ውጭ ግዛቶች',
        'Scotland': 'ስኮትላንድ', 'England': 'እንግሊዝ',
        'Holand-Netherlands': 'ኔዘርላንድ'
    },
    
    # ===== 8. SPANISH (Español) =====
    'spanish': {
        'United-States': 'Estados Unidos', 'Mexico': 'México',
        'Philippines': 'Filipinas', 'Germany': 'Alemania',
        'Canada': 'Canadá', 'Puerto-Rico': 'Puerto Rico',
        'El-Salvador': 'El Salvador', 'India': 'India',
        'United-Kingdom': 'Reino Unido', 'Japan': 'Japón',
        'Italy': 'Italia', 'Poland': 'Polonia', 'China': 'China',
        'Cuba': 'Cuba', 'Haiti': 'Haití',
        'Dominican-Republic': 'República Dominicana',
        'Nicaragua': 'Nicaragua', 'Honduras': 'Honduras',
        'Guatemala': 'Guatemala', 'France': 'Francia',
        'Taiwan': 'Taiwán', 'Jamaica': 'Jamaica',
        'Trinidad&Tobago': 'Trinidad y Tobago',
        'Ecuador': 'Ecuador', 'Peru': 'Perú',
        'South': 'Sur', 'Portugal': 'Portugal',
        'Ireland': 'Irlanda', 'Greece': 'Grecia',
        'Hungary': 'Hungría', 'Iran': 'Irán',
        'Columbia': 'Colombia', 'Cambodia': 'Camboya',
        'Thailand': 'Tailandia', 'Laos': 'Laos',
        'Vietnam': 'Vietnam', 'Hong': 'Hong Kong',
        'Yugoslavia': 'Yugoslavia',
        'Outlying-US(Guam-USVI-etc)': 'Territorios de EE.UU.',
        'Scotland': 'Escocia', 'England': 'Inglaterra',
        'Holand-Netherlands': 'Países Bajos'
    },
    
    # ===== 9. FRENCH (Français) =====
    'french': {
        'United-States': 'États-Unis', 'Mexico': 'Mexique',
        'Philippines': 'Philippines', 'Germany': 'Allemagne',
        'Canada': 'Canada', 'Puerto-Rico': 'Porto Rico',
        'El-Salvador': 'Salvador', 'India': 'Inde',
        'United-Kingdom': 'Royaume-Uni', 'Japan': 'Japon',
        'Italy': 'Italie', 'Poland': 'Pologne', 'China': 'Chine',
        'Cuba': 'Cuba', 'Haiti': 'Haïti',
        'Dominican-Republic': 'République dominicaine',
        'Nicaragua': 'Nicaragua', 'Honduras': 'Honduras',
        'Guatemala': 'Guatemala', 'France': 'France',
        'Taiwan': 'Taïwan', 'Jamaica': 'Jamaïque',
        'Trinidad&Tobago': 'Trinité-et-Tobago',
        'Ecuador': 'Équateur', 'Peru': 'Pérou',
        'South': 'Sud', 'Portugal': 'Portugal',
        'Ireland': 'Irlande', 'Greece': 'Grèce',
        'Hungary': 'Hongrie', 'Iran': 'Iran',
        'Columbia': 'Colombie', 'Cambodia': 'Cambodge',
        'Thailand': 'Thaïlande', 'Laos': 'Laos',
        'Vietnam': 'Viêt Nam', 'Hong': 'Hong Kong',
        'Yugoslavia': 'Yougoslavie',
        'Outlying-US(Guam-USVI-etc)': 'Territoires américains',
        'Scotland': 'Écosse', 'England': 'Angleterre',
        'Holand-Netherlands': 'Pays-Bas'
    },
    
    # ===== 10. JAPANESE (日本語) =====
    'japanese': {
        'United-States': 'アメリカ合衆国', 'Mexico': 'メキシコ',
        'Philippines': 'フィリピン', 'Germany': 'ドイツ',
        'Canada': 'カナダ', 'Puerto-Rico': 'プエルトリコ',
        'El-Salvador': 'エルサルバドル', 'India': 'インド',
        'United-Kingdom': 'イギリス', 'Japan': '日本',
        'Italy': 'イタリア', 'Poland': 'ポーランド', 'China': '中国',
        'Cuba': 'キューバ', 'Haiti': 'ハイチ',
        'Dominican-Republic': 'ドミニカ共和国',
        'Nicaragua': 'ニカラグア', 'Honduras': 'ホンジュラス',
        'Guatemala': 'グアテマラ', 'France': 'フランス',
        'Taiwan': '台湾', 'Jamaica': 'ジャマイカ',
        'Trinidad&Tobago': 'トリニダード・トバゴ',
        'Ecuador': 'エクアドル', 'Peru': 'ペルー',
        'South': '南', 'Portugal': 'ポルトガル',
        'Ireland': 'アイルランド', 'Greece': 'ギリシャ',
        'Hungary': 'ハンガリー', 'Iran': 'イラン',
        'Columbia': 'コロンビア', 'Cambodia': 'カンボジア',
        'Thailand': 'タイ', 'Laos': 'ラオス',
        'Vietnam': 'ベトナム', 'Hong': '香港',
        'Yugoslavia': 'ユーゴスラビア',
        'Outlying-US(Guam-USVI-etc)': '米国領土',
        'Scotland': 'スコットランド', 'England': 'イングランド',
        'Holand-Netherlands': 'オランダ'
    },
    
    # ===== 11. KOREAN (한국어) =====
    'korean': {
        'United-States': '미국', 'Mexico': '멕시코',
        'Philippines': '필리핀', 'Germany': '독일',
        'Canada': '캐나다', 'Puerto-Rico': '푸에르토리코',
        'El-Salvador': '엘살바도르', 'India': '인도',
        'United-Kingdom': '영국', 'Japan': '일본',
        'Italy': '이탈리아', 'Poland': '폴란드', 'China': '중국',
        'Cuba': '쿠바', 'Haiti': '아이티',
        'Dominican-Republic': '도미니카 공화국',
        'Nicaragua': '니카라과', 'Honduras': '온두라스',
        'Guatemala': '과테말라', 'France': '프랑스',
        'Taiwan': '타이완', 'Jamaica': '자메이카',
        'Trinidad&Tobago': '트리니다드 토바고',
        'Ecuador': '에콰도르', 'Peru': '페루',
        'South': '남쪽', 'Portugal': '포르투갈',
        'Ireland': '아일랜드', 'Greece': '그리스',
        'Hungary': '헝가리', 'Iran': '이란',
        'Columbia': '콜롬비아', 'Cambodia': '캄보디아',
        'Thailand': '태국', 'Laos': '라오스',
        'Vietnam': '베트남', 'Hong': '홍콩',
        'Yugoslavia': '유고슬라비아',
        'Outlying-US(Guam-USVI-etc)': '미국 해외 영토',
        'Scotland': '스코틀랜드', 'England': '잉글랜드',
        'Holand-Netherlands': '네덜란드'
    },
    
    # ===== 12. TURKISH (Türkçe) =====
    'turkish': {
        'United-States': 'Amerika Birleşik Devletleri', 'Mexico': 'Meksika',
        'Philippines': 'Filipinler', 'Germany': 'Almanya',
        'Canada': 'Kanada', 'Puerto-Rico': 'Porto Riko',
        'El-Salvador': 'El Salvador', 'India': 'Hindistan',
        'United-Kingdom': 'Birleşik Krallık', 'Japan': 'Japonya',
        'Italy': 'İtalya', 'Poland': 'Polonya', 'China': 'Çin',
        'Cuba': 'Küba', 'Haiti': 'Haiti',
        'Dominican-Republic': 'Dominik Cumhuriyeti',
        'Nicaragua': 'Nikaragua', 'Honduras': 'Honduras',
        'Guatemala': 'Guatemala', 'France': 'Fransa',
        'Taiwan': 'Tayvan', 'Jamaica': 'Jamaika',
        'Trinidad&Tobago': 'Trinidad ve Tobago',
        'Ecuador': 'Ekvador', 'Peru': 'Peru',
        'South': 'Güney', 'Portugal': 'Portekiz',
        'Ireland': 'İrlanda', 'Greece': 'Yunanistan',
        'Hungary': 'Macaristan', 'Iran': 'İran',
        'Columbia': 'Kolombiya', 'Cambodia': 'Kamboçya',
        'Thailand': 'Tayland', 'Laos': 'Laos',
        'Vietnam': 'Vietnam', 'Hong': 'Hong Kong',
        'Yugoslavia': 'Yugoslavya',
        'Outlying-US(Guam-USVI-etc)': 'ABD dış toprakları',
        'Scotland': 'İskoçya', 'England': 'İngiltere',
        'Holand-Netherlands': 'Hollanda'
    },
    
    # ===== 13. URDU (اردو) =====
    'urdu': {
        'United-States': 'ریاستہائے متحدہ امریکہ', 'Mexico': 'میکسیکو',
        'Philippines': 'فلپائن', 'Germany': 'جرمنی',
        'Canada': 'کینیڈا', 'Puerto-Rico': 'پورٹو ریکو',
        'El-Salvador': 'ایل سیلواڈور', 'India': 'بھارت',
        'United-Kingdom': 'برطانیہ', 'Japan': 'جاپان',
        'Italy': 'اٹلی', 'Poland': 'پولینڈ', 'China': 'چین',
        'Cuba': 'کیوبا', 'Haiti': 'ہیٹی',
        'Dominican-Republic': 'ڈومینیکن ریپبلک',
        'Nicaragua': 'نکاراگوا', 'Honduras': 'ہونڈوراس',
        'Guatemala': 'گوئٹے مالا', 'France': 'فرانس',
        'Taiwan': 'تائیوان', 'Jamaica': 'جمیکا',
        'Trinidad&Tobago': 'ٹرینیڈاڈ اور ٹوباگو',
        'Ecuador': 'ایکواڈور', 'Peru': 'پیرو',
        'South': 'جنوب', 'Portugal': 'پرتگال',
        'Ireland': 'آئرلینڈ', 'Greece': 'یونان',
        'Hungary': 'ہنگری', 'Iran': 'ایران',
        'Columbia': 'کولمبیا', 'Cambodia': 'کمبوڈیا',
        'Thailand': 'تھائی لینڈ', 'Laos': 'لاؤس',
        'Vietnam': 'ویتنام', 'Hong': 'ہانگ کانگ',
        'Yugoslavia': 'یوگوسلاویہ',
        'Outlying-US(Guam-USVI-etc)': 'امریکی بیرونی علاقے',
        'Scotland': 'سکاٹ لینڈ', 'England': 'انگلینڈ',
        'Holand-Netherlands': 'نیدرلینڈز'
    },
    
    # ===== 14. SWAHILI (Kiswahili) =====
    'swahili': {
        'United-States': 'Marekani', 'Mexico': 'Meksiko',
        'Philippines': 'Ufilipino', 'Germany': 'Ujerumani',
        'Canada': 'Kanada', 'Puerto-Rico': 'Puerto Rico',
        'El-Salvador': 'El Salvador', 'India': 'Uhindi',
        'United-Kingdom': 'Uingereza', 'Japan': 'Ujapani',
        'Italy': 'Italia', 'Poland': 'Poland', 'China': 'Uchina',
        'Cuba': 'Kuba', 'Haiti': 'Haiti',
        'Dominican-Republic': 'Jamhuri ya Dominikana',
        'Nicaragua': 'Nikaragua', 'Honduras': 'Honduras',
        'Guatemala': 'Guatemala', 'France': 'Ufaransa',
        'Taiwan': 'Taiwan', 'Jamaica': 'Jamaika',
        'Trinidad&Tobago': 'Trinidad na Tobago',
        'Ecuador': 'Ekwado', 'Peru': 'Peru',
        'South': 'Kusini', 'Portugal': 'Ureno',
        'Ireland': 'Ayalandi', 'Greece': 'Ugiriki',
        'Hungary': 'Hungaria', 'Iran': 'Uajemi',
        'Columbia': 'Kolombia', 'Cambodia': 'Kambodia',
        'Thailand': 'Thailand', 'Laos': 'Laos',
        'Vietnam': 'Vietnam', 'Hong': 'Hong Kong',
        'Yugoslavia': 'Yugoslavia',
        'Outlying-US(Guam-USVI-etc)': 'Maeneo ya nje ya Marekani',
        'Scotland': 'Uskoti', 'England': 'Uingereza',
        'Holand-Netherlands': 'Uholanzi'
    }
}

# See PART 1 for the full country_translations dictionary
# (In the full script, paste the country_translations from earlier)

# ============================================================
# 12. GENERATE ALL TRANSLATED FILES
# ============================================================

languages = ['chinese', 'arabic', 'hindi', 'russian', 'greek', 'portuguese',
             'amharic', 'spanish', 'french', 'japanese', 'korean', 'turkish',
             'urdu', 'swahili']

output_dir = "census_translations"
os.makedirs(output_dir, exist_ok=True)

for lang in languages:
    df_lang = df.copy()
    
    # Apply categorical translations
    df_lang['workclass'] = df_lang['workclass'].map(workclass_maps[lang])
    df_lang['education'] = df_lang['education'].map(education_maps[lang])
    df_lang['marital-status'] = df_lang['marital-status'].map(marital_maps[lang])
    df_lang['occupation'] = df_lang['occupation'].map(occupation_maps[lang])
    df_lang['relationship'] = df_lang['relationship'].map(relationship_maps[lang])
    df_lang['race'] = df_lang['race'].map(race_maps[lang])
    df_lang['sex'] = df_lang['sex'].map(sex_maps[lang])
    df_lang['income'] = df_lang['income'].map(income_maps[lang])
    
    # Apply country translations
    df_lang['native-country'] = df_lang['native-country'].map(country_translations[lang])
    
    # Apply header translations
    df_lang.rename(columns=header_maps[lang], inplace=True)
    
    # Save CSV
    filename = f"{output_dir}/adult_census_{lang}.csv"
    df_lang.to_csv(filename, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_NONNUMERIC)
    print(f"✅ {lang.capitalize()} translation complete! ({len(df_lang)} rows)")

