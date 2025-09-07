export interface Sphere {
  id: string;
  name: string;
  emoji: string;
}

export const SPHERES: Record<string, Sphere> = {
  love: { id: "love", name: "Отношения с любимыми", emoji: "💖" },
  family: { id: "family", name: "Отношения с родными", emoji: "🏡" },
  friends: { id: "friends", name: "Друзья", emoji: "🤝" },
  career: { id: "career", name: "Карьера", emoji: "💼" },
  physical: { id: "physical", name: "Физическое здоровье", emoji: "♂️" },
  mental: { id: "mental", name: "Ментальное здоровье", emoji: "🧠" },
  hobby: { id: "hobby", name: "Хобби и увлечения", emoji: "🎨" },
  wealth: { id: "wealth", name: "Благосостояние", emoji: "💰" },
};

// Экспортируем массив для сохранения канонического порядка
export const SPHERE_ORDERED: Sphere[] = [
  SPHERES.love,
  SPHERES.family,
  SPHERES.friends,
  SPHERES.career,
  SPHERES.physical,
  SPHERES.mental,
  SPHERES.hobby,
  SPHERES.wealth,
]; 