// Структура данных для таймлайна "Мой путь"
// в соответствии с docs/way.md

export type HpiMetric = {
  sphere: string; // эмодзи-сфера
  value: number;
  reason?: string;
};

export type CardNode = {
  id: string;
  type: 'work' | 'life';
  category: 'career' | 'hobby' | 'family' | 'health';
  title: string;
  period: string; // "YYYY-YYYY" или "YYYY"
  hpi_metrics?: HpiMetric[];
};

export const nodes: CardNode[] = [
  // Work nodes
  { id: 'law-edu', type: 'work', category: 'career', title: 'Юридическое образование', period: '2005-2007', hpi_metrics: [{ sphere: '💼', value: 1 }] },
  { id: 'analyst-gov', type: 'work', category: 'career', title: 'Аналитик в Гос.проектах', period: '2007-2011', hpi_metrics: [{ sphere: '💼', value: 1 }] },
  { id: 'gov-management', type: 'work', category: 'career', title: 'Управление в Гос. проектах', period: '2012-2017', hpi_metrics: [{ sphere: '💼', value: 1 }, { sphere: '💰', value: 1 }] },
  { id: 'higher-law', type: 'work', category: 'career', title: 'Высшее юридическое образование', period: '2008-2012', hpi_metrics: [{ sphere: '💼', value: 1 }] },
  { id: 'vink', type: 'work', category: 'career', title: 'Руководство ИТ проектами в VINK.RU', period: '2018-2019', hpi_metrics: [{ sphere: '💼', value: 1 }, { sphere: '💰', value: 1 }] },
  { id: 'teaching', type: 'work', category: 'career', title: 'Педагогический опыт', period: '2019-2021', hpi_metrics: [{ sphere: '💼', value: 1 }] },
  { id: 'robius-ceo', type: 'work', category: 'career', title: 'CEO в ROBIUS-IT.RU', period: '2019-2022', hpi_metrics: [{ sphere: '💼', value: 1 }] },
  { id: 'magistratura', type: 'work', category: 'career', title: 'Магистратура "Системный анализ и управление"', period: '2022-2025', hpi_metrics: [{ sphere: '💼', value: 1 }] },
  { id: 'svo', type: 'work', category: 'career', title: 'Руководитель ИТ проектов для AO "Международный аэропорт Шереметьево" (CD-IT.RU)', period: '2023-2024', hpi_metrics: [{ sphere: '💼', value: 1 }, { sphere: '💰', value: 1 }] },
  { id: 'mba', type: 'work', category: 'career', title: 'MBA по инновациям', period: '2023-2024', hpi_metrics: [{ sphere: '💼', value: 1 }] },
  // Life nodes
  { id: 'sport-wushu', type: 'life', category: 'hobby', title: 'Спорт УШУ Саньда', period: '2002', hpi_metrics: [{ sphere: '🎨', value: 1 }, { sphere: '♂️', value: 1 }] },
  { id: 'coach-wushu', type: 'life', category: 'hobby', title: 'Тренер УШУ Саньда', period: '2008', hpi_metrics: [{ sphere: '🎨', value: 1 }] },
  { id: 'family-create', type: 'life', category: 'family', title: 'Создание семьи', period: '2008', hpi_metrics: [{ sphere: '🏡', value: 1 }] },
  { id: 'philosophy', type: 'life', category: 'hobby', title: 'Увлечение философией и историей', period: '2008', hpi_metrics: [{ sphere: '🧠', value: 1 }] },
  { id: 'child1', type: 'life', category: 'family', title: 'Родился ребенок', period: '2009', hpi_metrics: [{ sphere: '🏡', value: 1 }] },
  { id: 'child2', type: 'life', category: 'family', title: 'Родился второй ребенок', period: '2014', hpi_metrics: [{ sphere: '🏡', value: 1 }] },
  { id: 'robius', type: 'life', category: 'hobby', title: 'Личный проект ROBIUS.RU', period: '2015', hpi_metrics: [{ sphere: '🎨', value: 1 }] },
  { id: 'phd', type: 'life', category: 'hobby', title: 'Научная деятельность в аспирантуре', period: '2016', hpi_metrics: [{ sphere: '🎨', value: 1 }] },
  { id: 'child3', type: 'life', category: 'family', title: 'Родился третий ребенок', period: '2016', hpi_metrics: [{ sphere: '🏡', value: 1 }] },
  { id: 'move-spb', type: 'life', category: 'family', title: 'Переезд в СПБ', period: '2018', hpi_metrics: [{ sphere: '🏡', value: 1 }, { sphere: '🧠', value: -1 }] },
  { id: 'meditation', type: 'life', category: 'health', title: 'Начало медитации', period: '2022', hpi_metrics: [{ sphere: '♂️', value: 1 }] },
  { id: 'move-msk', type: 'life', category: 'family', title: 'Переезд в Москву', period: '2023', hpi_metrics: [{ sphere: '🧠', value: -1 }] },
  { id: 'hpi-concept', type: 'life', category: 'hobby', title: 'Разработка концепта HPI', period: '2024', hpi_metrics: [{ sphere: '🎨', value: 1 }] },
  { id: 'hpi-mvp', type: 'life', category: 'hobby', title: 'Разработка MVP HPI', period: '2025', hpi_metrics: [{ sphere: '🎨', value: 1 }, { sphere: '💼', value: 1 }] },
]; 