# Дизайн-система HPI.expert

## 1. Фирменные цвета

| Назначение         | Цвет      | HEX      |
|--------------------|-----------|----------|
| Основной синий     | Blue      | #0A2463  |
| Акцентный красный  | Red       | #FB3640  |
| Вторичный бежевый  | Beige     | #E0CBA8  |
| Фоновый светлый    | Light Gray| #F7F8FA  |

> **Акцентный красный (#FB3640) выбран как единственный фирменный красный.** Он используется для кнопок, ссылок, акцентов и уведомлений. Не используйте другие оттенки красного для акцентов.

**Примеры использования:**
- Кнопки: фон, hover, active
- Подчеркивание активных ссылок
- Иконки предупреждений и ошибок

## 2. Кнопки

В проекте используются три основных вида кнопок:

### 2.1. Продающие (Primary, CTA)
- **Цвет:** Красный (#FB3640)
- **Текст:** Белый
- **Использование:** Главные действия, призывы к покупке, регистрации, началу работы, отправке формы.
- **Примеры:** «Войти», «Запросить демо», «Начать бесплатно»
- **CSS-класс:** `.ctaButton`, `.loginButton`

```html
<button class="ctaButton">Запросить демо</button>
```

### 2.2. Помогающие/Ведущие (Secondary)
- **Цвет:** Синий (#0A2463)
- **Текст:** Белый
- **Использование:** Вспомогательные действия, переходы по пользовательскому пути, «Подробнее», «Перейти», «Следующий шаг»
- **Примеры:** «Перейти в дашборд», «Подробнее», «К списку»
- **CSS-класс:** `.dashboardButton`

```html
<button class="dashboardButton">Перейти в дашборд</button>
```

### 2.3. Дополнительные/Фактические (Tertiary)
- **Цвет:** Коричневый/бежевый (#E0CBA8)
- **Текст:** Чёрный или тёмно-серый (#333)
- **Использование:** Второстепенные действия, подтверждения, кнопки-факты, не ведущие к ключевым событиям.
- **Примеры:** «Скачать PDF», «Показать ещё», «Сбросить», «Результаты»
- **CSS-класс:** `.secondaryButton`

```html
<button class="secondaryButton">Скачать PDF</button>
```

---

- **Disabled-состояние:** Любая кнопка может быть неактивной (серый фон, opacity: 0.5, cursor: not-allowed).
- **Outline-стиль:** Для вторичных/дополнительных кнопок можно использовать прозрачный фон и цветную рамку.
- **Иконки:** Для навигационных и дополнительных кнопок можно добавлять иконки слева/справа.

### Примеры CSS для кнопок

```css
.ctaButton, .loginButton {
  background: #FB3640;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  height: 40px;
  padding: 0 24px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s, box-shadow 0.2s;
}
.ctaButton:hover, .loginButton:hover {
  background: #e13c3e; /* Этот цвет тоже нужно будет скорректировать */
  box-shadow: 0 2px 8px rgba(251,54,64,0.15);
}

.dashboardButton {
  background: #0A2463;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  height: 40px;
  padding: 0 24px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s, box-shadow 0.2s;
}
.dashboardButton:hover {
  background: #081a45;
  box-shadow: 0 2px 8px rgba(10,36,99,0.12);
}

.secondaryButton {
  background: #E0CBA8;
  color: #333;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  height: 40px;
  padding: 0 24px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s, box-shadow 0.2s;
}
.secondaryButton:hover {
  background: #d2b98f;
  box-shadow: 0 2px 8px rgba(224,203,168,0.15);
}

button:disabled, .ctaButton:disabled, .dashboardButton:disabled, .secondaryButton:disabled {
  background: #ccc;
  color: #888;
  cursor: not-allowed;
  opacity: 0.5;
  box-shadow: none;
}
```

## 3. Блоки и секции

### 3.1. Общие правила
- **Максимальная ширина:** 1200px
- **Внешние отступы между секциями:** 48px
- **Внутренние отступы (padding):** 32px (минимум)
- **Фон:** #fff (карточки), #F7F8FA (основной фон), #0A2463 (шапка), #E0CBA8 (футер)
- **Скругление:** 8–16px (карточки, модалки)
- **Тень:** 0 2px 8px rgba(10,36,99,0.06) (карточки, модалки)
- **Горизонтальные отступы:** 16–32px (на мобильных — 16px)
- **Адаптивность:** на мобильных padding уменьшается до 16px, max-width: 100%

### 3.2. Карточки (card)
- **Фон:** #fff
- **Скругление:** 16px
- **Тень:** 0 4px 6px rgba(0,0,0,0.1)
- **Внутренний padding:** 32px (2rem)
- **Минимальная ширина:** 300px
- **Максимальная ширина:** 400px
- **Отступ между карточками:** 32px

```css
.card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  padding: 2rem;
  min-width: 300px;
  max-width: 400px;
  margin: 0 16px 32px 0;
}
```

### 3.3. Секции (section)
- **Фон:** #F7F8FA или #fff
- **Внешний отступ снизу:** 48px
- **Внутренний padding:** 32px

### 3.4. Меню и навигация
- **Фон:** #0A2463 (шапка), #fff (боковое меню)
- **Скругление:** 0 (шапка), 12px (боковое меню)
- **Тень:** только у выпадающих меню

### 3.5. Футер (пример)

Футер оформляется как единый контейнер с фоном #E0CBA8, выравниванием по центру, крупными иконками и фирменным синим текстом.

```jsx
<footer className="footer">
  <div className="footerIcons">
    <a href="mailto:88@robius.ru" aria-label="Email"><i className="icon-mail"></i></a>
    <a href="https://t.me/hpi_expert" target="_blank" rel="noopener noreferrer" aria-label="Telegram"><i className="icon-telegram"></i></a>
    <a href="https://www.linkedin.com/company/hpi-expert/" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><i className="icon-linkedin"></i></a>
  </div>
  <div className="footerCopyright">
    © 2025 HPI.EXPERT<br />
    Разработано <a href="https://robius.ru" target="_blank" rel="noopener noreferrer">ROBIUS IT</a>
  </div>
</footer>
```

- **Фон:** #E0CBA8
- **Текст и иконки:** #0A2463
- **Иконки:** 2rem, с плавным hover-эффектом (красный #FF4D4F)
- **Выравнивание:** по центру
- **Без лишних линий и теней**

## 4. Отступы

- **Внешние отступы между секциями:** 48px
- **Внутренние отступы в блоках:** 32px
- **Отступы между элементами в строке:** 24–32px

## 5. Заголовки и текст

- **H1:** 2.5rem (40px), font-weight: 700
- **H2:** 2rem (32px), font-weight: 600
- **H3:** 1.5rem (24px), font-weight: 500
- **Текст:** 1rem (16px), font-weight: 400

---

> _Этот документ — основа для будущей дизайн-системы. Здесь фиксируются все ключевые параметры оформления фронта HPI.expert._ 