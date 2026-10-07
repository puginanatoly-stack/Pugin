# Модель роста и протухания памяти агента ZCode/GLM. Данные: ПРОГНОЗ-колапс-памяти (07.10.2026).
import math
W=200_000; F0=69; T0=2.5            # файлов за 2.5 недели
TOK_PER_FILE=11_000/F0              # ~159 ток. индекса на файл (85 строк / 69 файлов)
weeks={'01.2027':12.5,'04.2027':25.5,'10.2027':51.5}
def lin(r): return lambda t: F0+r*t
def powr(b):                        # N(t)=a*(T0+t)^b, проходит через 69 при t=0
    a=F0/T0**b; return lambda t: a*(T0+t)**b
sc={'агент 20/нед':lin(20),'факт 27.6/нед':lin(F0/T0),'степ. b=0.7':powr(0.7),'степ. b=0.5':powr(0.5)}
print('Сценарий            | '+' | '.join(f'{k:>16}' for k in weeks))
for n,f in sc.items():
    print(f'{n:19} | '+' | '.join(f'{f(t):5.0f}ф {f(t)*TOK_PER_FILE/1000:4.0f}k {f(t)*TOK_PER_FILE/W*100:3.0f}%' for t in weeks.values()))
print('\nНеделя, когда индекс займёт 15/25/40% окна:')
for n,f in sc.items():
    out=[]
    for p in (.15,.25,.40):
        t=next((t for t in range(0,600) if f(t)*TOK_PER_FILE>=p*W),None); out.append(f'{p:.0%}: нед.{t}' if t is not None else f'{p:.0%}: >11 лет')
    print(f'  {n:19} '+', '.join(out))
# Протухание: приток постоянный, полураспад h, доля протухших (p_valid<0.5 трактуем ожиданием)
print('\nДоля неверных среди volatile-фактов через T дней (приток постоянный):')
for h in (30,45,60,90):
    row=[]
    for T in (90,180,365):
        valid=(h/(T*math.log(2)))*(1-2**(-T/h)); row.append(f'T={T}: {1-valid:4.0%}')
    print(f'  h={h:3}д  '+'  '.join(row))
# Точка безубыточности строки индекса
print('\nСтрока индекса окупается, если её используют хотя бы раз в N дней:')
for L in (60,130,250):           # токенов в строке
  for S in (5_000,20_000):        # сэкономлено на одном попадании
    for sess in (5,15):           # сеансов в день
        print(f'  строка {L:3} ток, экономия {S//1000:2}k, {sess:2} сеанс/д -> раз в {S/(L*sess):5.1f} дн.')
# Шум поиска: максимум N нерелевантных косинусов ~ mu + sigma*sqrt(2 ln N)
mu,sg=0.45,0.08
print('\nОжидаемый лучший НЕрелевантный скор (mu=0.45, sigma=0.08, оценка для bge-m3):')
for N in (100,367,1000,5000,20000): print(f'  N={N:6}: {mu+sg*math.sqrt(2*math.log(N)):.2f}')
