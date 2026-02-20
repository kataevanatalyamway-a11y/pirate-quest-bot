# stages.py
from datetime import datetime

# Тексты для каждого этапа (на двух языках)
STAGES = {
    'ru': [
        {
            'title': 'Форт Сан-Лоренсу',
            'description': 'Старая крепость, где держали пленных пиратов. Капитан Тейлор спрятал здесь первый фрагмент карты.',
            'task': 'Найди пушку с вензелем и сфотографируй её.',
            'location': {'lat': 32.6485, 'lon': -16.9085},  # координаты форта
            'hint': 'Пушка находится на нижнем ярусе, у самой воды.',
            'photo': 'fort_sao_lorenzo.jpg'  # можно отправить фото для ориентира
        },
        {
            'title': 'Старый город (Zona Velha)',
            'description': 'В 18 веке здесь была таверна "Морской волк", где пираты пропивали добычу.',
            'task': 'Найди дверь с изображением рыбы (их там много, выбери самую красивую).',
            'location': {'lat': 32.6475, 'lon': -16.9040},
            'hint': 'Ищи на Rua de Santa Maria, там все двери разрисованы.',
            'photo': 'zona_velha_door.jpg'
        },
        {
            'title': 'Рынок Лаврадор',
            'description': 'Здесь капитан покупал припасы перед плаванием. Один из торговцев был его информатором.',
            'task': 'Найди прилавок с самой большой рыбой (скульптура или настоящая).',
            'location': {'lat': 32.6490, 'lon': -16.9055},
            'hint': 'На рынке есть большой макет рыбы, его сложно не заметить.',
            'photo': 'mercado_dos_lavradores.jpg'
        },
        {
            'title': 'Мыс Гиран (Cabo Girão)',
            'description': 'С этого утёса пираты высматривали торговые корабли.',
            'task': 'Встань на стеклянный пол и сфотографируй вид вниз.',
            'location': {'lat': 32.6560, 'lon': -17.0040},
            'hint': 'Стеклянная смотровая площадка находится прямо над обрывом.',
            'photo': 'cabo_girao.jpg'
        },
        {
            'title': 'Камара-де-Лобуш',
            'description': 'Рыбацкая деревня, где капитан спрятал последнюю часть карты перед отплытием.',
            'task': 'Найди старую рыбацкую лодку и сфотографируй её на фоне океана.',
            'location': {'lat': 32.6415, 'lon': -16.9775},
            'hint': 'Лодки стоят прямо на пляже, у ресторанов.',
            'photo': 'camara_de_lobos.jpg'
        }
    ],
    'en': [
        {
            'title': 'Fort São Lourenço',
            'description': 'The old fortress where pirates were imprisoned. Captain Taylor hid the first piece of the map here.',
            'task': 'Find the cannon with the monogram and take a photo of it.',
            'location': {'lat': 32.6485, 'lon': -16.9085},
            'hint': 'The cannon is on the lower level, near the water.',
            'photo': 'fort_sao_lorenzo.jpg'
        },
        {
            'title': 'Old Town (Zona Velha)',
            'description': 'In the 18th century, there was a tavern "Sea Wolf" here, where pirates spent their loot.',
            'task': 'Find a door with a fish painting (there are many, choose the most beautiful one).',
            'location': {'lat': 32.6475, 'lon': -16.9040},
            'hint': 'Look on Rua de Santa Maria, all doors there are painted.',
            'photo': 'zona_velha_door.jpg'
        },
        {
            'title': 'Lavradores Market',
            'description': 'The captain bought supplies here before sailing. One of the traders was his informant.',
            'task': 'Find the stall with the biggest fish (sculpture or real).',
            'location': {'lat': 32.6490, 'lon': -16.9055},
            'hint': 'There is a large fish model at the market, hard to miss.',
            'photo': 'mercado_dos_lavradores.jpg'
        },
        {
            'title': 'Cabo Girão',
            'description': 'From this cliff, pirates watched for merchant ships.',
            'task': 'Stand on the glass floor and take a photo of the view down.',
            'location': {'lat': 32.6560, 'lon': -17.0040},
            'hint': 'The glass viewing platform is right above the cliff.',
            'photo': 'cabo_girao.jpg'
        },
        {
            'title': 'Câmara de Lobos',
            'description': 'A fishing village where the captain hid the last part of the map before sailing.',
            'task': 'Find an old fishing boat and photograph it against the ocean.',
            'location': {'lat': 32.6415, 'lon': -16.9775},
            'hint': 'Boats are right on the beach, near the restaurants.',
            'photo': 'camara_de_lobos.jpg'
        }
    ]
}

def get_stage_text(lang, stage_num, key):
    """Получить текст этапа по языку, номеру и ключу"""
    if lang not in STAGES:
        lang = 'ru'
    if stage_num < 1 or stage_num > len(STAGES[lang]):
        return None
    return STAGES[lang][stage_num-1].get(key, '')

def get_stage_location(lang, stage_num):
    """Получить координаты этапа"""
    if lang not in STAGES:
        lang = 'ru'
    if stage_num < 1 or stage_num > len(STAGES[lang]):
        return None
    return STAGES[lang][stage_num-1].get('location')