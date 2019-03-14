
##################################################################################################################
### GENERAL WORKOUT GENERATOR

GENERAL_MUSCLES = [
    ('CHEST','Грудь'),
    ('BACK','Спина'),
    ('LEGS','Ноги'),
    ('BICEPS','Бицепс'),
    ('TRICEPS','Трицепс'),
    ('SHOULDERS','Плечи'),
    ('ABS','Пресс'),
    ('BICEPS_BEDRA','Бицепс бедра'),
    ('KVADRICEPS','Квадрицепс'),
    ('MIDDLE_DELTA','Средняя дельта'),
    ('BACK_DELTA','Задняя дельта'),
    ('LOIN','Поясница'),  # Поясница
    ('BUTT','Ягодицы'),  # Ягодицы
    ('RHOMBOID','Ромбовидные'),  # Ромбовидные
    ('CARDIO','Кардио'),
    ('BROADEST','Широчайшие'),   # Широчайшие
]

##################################################################################################################
## MALE NEWBIES

M_N = {
    'workout1':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':10
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':12
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'CHEST', 'rep':12
            },
            'training2':{
                'cat1':'Функциональное', 'cat3':'CHEST', 'rep':10
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':10
            },'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'LEGS', 'rep':12
            },'approach':3,
        },
        'set5':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BICEPS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'TRICEPS', 'rep':15
            },'approach':3,
        },
    },
    'workout2':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BACK', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'SHOULDERS', 'rep':12
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':15
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':15
            },'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'LEGS', 'rep':15
            },'approach':3,
        },
        'set5':{
            'training1':{
                'cat1':'Статическое', 'cat3':'ABS', 'rep':'1 мин'
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'ABS', 'rep':20
            }, 'approach':3,
        },
    },
    'workout3':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':12
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'CHEST', 'rep':15
            },
            'training2':{
                'cat1':'Функциональное', 'cat3':'BACK', 'rep':12
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':15
            },'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BICEPS_BEDRA', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'KVADRICEPS', 'rep':15
            },'approach':3,
        },
        'set5':{
            'training1':{
                'cat1':'Базовое','cat2':'Тренажер', 'cat3':'BACK', 'rep':10
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BICEPS', 'rep':12
            }, 'approach':3,
        },
    },
}

##################################################################################################################
## MALE MIDDLES

M_M = {
    'workout1':{
        'set1':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'CHEST', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'MIDDLE_DELTA', 'rep':15
            }, 'approach':5,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':12
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':15
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'CHEST', 'rep':15
            },
            'training2':{
                'cat1':'Функциональное',  'cat3':'SHOULDERS', 'rep':15
            }, 'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':12
            },
            'training2':{
                'cat1':'Статическое', 'cat3':'ABS', 'rep':'1 мин'
            },
            'approach':3,
        },
        'set5':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'LEGS', 'rep':10
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'LOIN', 'rep':10
            }, 'approach':4,
        },
    },
    'workout2':{
        'set1':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':12
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Собственный', 'cat3':'BACK', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'MIDDLE_DELTA', 'rep':15
            }, 'approach':4,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BACK', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'KVADRICEPS', 'rep':15
            },'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'LEGS', 'rep':12
            },'approach':4,
        },
        'set5':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BICEPS', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'ABS', 'rep':20
            },'approach':3,
        },
    },
    'workout3':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':12
            },'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':15
            },
            'training2':{
                'cat1':'Базовое',  'cat2':'Собственный', 'cat3':'BACK', 'rep':8
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'LEGS', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'CHEST', 'rep':12
            },
            'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'TRICEPS', 'rep':15
            },'approach':3,
        },
        'set5':{
            'training1':{
                'cat1':'Изолированное','cat2':'Свободный', 'cat3':'BICEPS', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'TRICEPS', 'rep':15
            }, 'approach':3,
        },
    },
}


##################################################################################################################
## MALE ADVANCED

M_A = {
    'workout1':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':12
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Собственный', 'cat3':'BACK', 'rep':12
            }, 'approach':4,
        },
        'set2':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'CHEST', 'rep':20
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':15
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':15
            }, 'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'TRICEPS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BICEPS', 'rep':20
            },
            'approach':4,
        },
        'set5':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'TRICEPS', 'rep':20
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BICEPS', 'rep':20
            }, 'approach':4,
        },
    },
    'workout2':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':12
            },
            'approach':5,
        },
        'set2':{
            'training1':{
                'cat1':'Статическое', 'cat3':'LEGS', 'rep':'45 сек'
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер','cat3':'KVADRICEPS', 'rep':15
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'KVADRICEPS', 'rep':15
            },'approach':4,
        },
        'set4':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'MIDDLE_DELTA', 'rep':15
            },'approach':4,
        },
        'set5':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'SHOULDERS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BACK_DELTA', 'rep':20
            },'approach':4,
        },
    },
    'workout3':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'CHEST', 'rep':18
            },
            'training2':{
                'cat1':'Базовое',  'cat2':'Собственный', 'cat3':'BACK', 'rep':15
            }, 'approach':4,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное',  'cat2':'Свободный', 'cat3':'MIDDLE_DELTA', 'rep':20
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'CHEST', 'rep':15
            },
            'training3':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'MIDDLE_DELTA', 'rep':15
            },
            'approach':4,
        },
        'set4':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'TRICEPS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BICEPS', 'rep':15
            },
            'training3':{
                'cat1':'Функциональное', 'cat3':'TRICEPS', 'rep':10
            },'approach':4,
        },
        'set5':{
            'training1':{
                'cat1':'Статическое','cat3':'ABS', 'rep':'1 мин'
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'ABS', 'rep':20
            }, 'approach':3,
        },
    },
}


##################################################################################################################
## FEMALE NEWBIES

F_N = {
    'workout1':{
        'set1':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BUTT', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BUTT', 'rep':20
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BICEPS_BEDRA', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'LOIN', 'rep':10
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Статическое', 'cat3':'ABS', 'rep':'40 сек'
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Собственный', 'cat3':'BICEPS_BEDRA', 'rep':15
            },'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'RHOMBOID', 'rep':10
            },'approach':3,
        },
        'set5':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'ABS', 'rep':15
            },'approach':3,
        },
    },
    'workout2':{
        'set1':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'LOIN', 'rep':10
            },
            'training2':{
                'cat1':'Функциональное','cat3':'CHEST', 'rep':10
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':12
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BICEPS_BEDRA', 'rep':10
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'BACK', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':12
            },'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Функциональное', 'cat2':'Кардио',  'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'ABS', 'rep':20
            },'approach':3,
        },
    },
    'workout3':{
        'set1':{
            'training1':{
                'cat1':'Статическое',  'cat3':'LEGS', 'rep':'45 сек'
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':12
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BICEPS_BEDRA', 'rep':12
            },
            'training2':{
                'cat1':'Изолированное', 'cat3':'Тренажер', 'cat3':'LOIN', 'rep':12
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Функциональное', 'cat3':'SHOULDERS', 'rep':12
            },
            'training2':{
                'cat1':'Функциональное', 'cat2':'Кардио', 'rep':12
            },
            'training3':{
                'cat1':'Функциональное', 'cat3':'CHEST', 'rep':12
            },'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Статическое',  'cat3':'ABS', 'rep':'40 сек'
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'ABS', 'rep':15
            },'approach':3,
        },
    },
}

##################################################################################################################
## FEMALE MIDDLES

F_M = {
    'workout1':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BICEPS_BEDRA', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BUTT', 'rep':20
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BUTT', 'rep':20
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'LEGS', 'rep':15
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BUTT', 'rep':20
            }, 'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Функциональное', 'cat3':'BACK', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'ABS', 'rep':20
            },
            'training3':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'LOIN', 'rep':12
            },
            'approach':3,
        },
    },
    'workout2':{
        'set1':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BROADEST', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':12
            }, 'approach':3,
        },
        'set2':{
            'training1':{
                'cat1':'Функциональное',  'cat3':'SHOULDERS', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Собственный', 'cat3':'BROADEST', 'rep':12
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'BROADEST', 'rep':12
            },'approach':3,
        },
        'set4':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'LOIN', 'rep':15
            },
            'training2':{
                'cat1':'Функциональное',  'cat3':'ABS', 'rep':15
            },
            'training3':{
                'cat1':'Базовое', 'cat2':'Собственный', 'cat3':'CHEST', 'rep':12
            },'approach':3,
        },
    },
    'workout3':{
        'set1':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BUTT', 'rep':20
            },'approach':5,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':15
            },
            'training2':{
                'cat1':'Базовое',  'cat2':'Свободный', 'cat3':'BUTT', 'rep':20
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BUTT', 'rep':25
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BICEPS_BEDRA', 'rep':15
            },
            'approach':4,
        },
        'set4':{
            'training1':{
                'cat1':'Функциональное',  'cat3':'SHOULDERS', 'rep':20
            },
            'training2':{
                'cat1':'Функциональное',  'cat3':'ABS', 'rep':20
            },'approach':3,
        },
        'set5':{
            'training1':{
                'cat1':'Базовое','cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BROADEST', 'rep':15
            }, 'approach':3,
        },
    },
}


##################################################################################################################
## FEMALE ADVANCED

F_A = {
    'workout1':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BUTT', 'rep':20
            }, 'approach':4,
        },
        'set2':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BUTT', 'rep':25
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BICEPS_BEDRA', 'rep':15
            }, 'approach':4,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'LEGS', 'rep':18
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'BUTT', 'rep':20
            }, 'approach':4,
        },
        'set4':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Собственный', 'cat3':'BROADEST', 'rep':12
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':15
            },
            'approach':4,
        },
    },
    'workout2':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BROADEST', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Свободный', 'cat3':'SHOULDERS', 'rep':15
            },
            'approach':4,
        },
        'set2':{
            'training1':{
                'cat1':'Изолированное','cat2':'Тренажер', 'cat3':'BROADEST', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный','cat3':'SHOULDERS', 'rep':15
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'BROADEST', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':12
            },'approach':4,
        },
        'set4':{
            'training1':{
                'cat1':'Функциональное',  'cat3':'SHOULDERS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Собственный', 'cat3':'ABS', 'rep':25
            },'approach':3,
        },
    },
    'workout3':{
        'set1':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'BICEPS_BEDRA', 'rep':18
            },
            'training2':{
                'cat1':'Изолированное',  'cat2':'Тренажер', 'cat3':'BUTT', 'rep':25
            }, 'approach':5,
        },
        'set2':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'LEGS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное',  'cat2':'Свободный', 'cat3':'BUTT', 'rep':20
            }, 'approach':3,
        },
        'set3':{
            'training1':{
                'cat1':'Базовое', 'cat2':'Тренажер', 'cat3':'LEGS', 'rep':15
            },
            'training2':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BICEPS_BEDRA', 'rep':15
            },
            'approach':4,
        },
        'set4':{
            'training1':{
                'cat1':'Изолированное', 'cat2':'Тренажер', 'cat3':'BROADEST', 'rep':15
            },
            'training2':{
                'cat1':'Базовое', 'cat2':'Свободный', 'cat3':'CHEST', 'rep':15
            },
            'approach':3,
        },
    },
}

##################################################################################################################
### GENERAL FOODPROGRAM GENERATOR











