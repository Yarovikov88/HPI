import React, { useState, useEffect, useRef } from 'react';
import styles from './GetProPage.module.css';
import { apiClient } from '../services/api';
import { useAuth } from '../hooks/useAuth';

export default function GetProPage() {
  const { user, refreshProfile } = useAuth();
  const [selectedOption, setSelectedOption] = useState<'referrals' | 'share' | 'feedback' | null>(null);
  const [feedbackMethod, setFeedbackMethod] = useState<'site' | 'bot' | null>(null);
  const [referrals, setReferrals] = useState(['', '']);
  const [feedbackForm, setFeedbackForm] = useState({ type: 'bug', message: '', image: null as File | null });
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [shareUtm, setShareUtm] = useState<string>('');
  const [feedbackCount, setFeedbackCount] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Генерируем уникальную UTM-метку для пользователя при каждом рендере
  useEffect(() => {
    if (user?.id) {
      // Создаем уникальную UTM-метку с ID пользователя и текущим временем
      const utm = `user_${user.id}_${Date.now()}`;
      setShareUtm(utm);
      console.log(`Создана UTM-метка для пользователя ${user.id}: ${utm}`);
    }
  }, [user?.id, selectedOption]); // Генерируем новую UTM при выборе опции "share"

  const handleReferralChange = (index: number, value: string) => {
    const newReferrals = [...referrals];
    newReferrals[index] = value;
    setReferrals(newReferrals);
  };

  const handleReferralSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setSubmitting(true);
    
    if (referrals.some(r => r.trim() === '')) {
      setMessage({ type: 'error', text: 'Пожалуйста, заполните оба поля для приглашений.' });
      setSubmitting(false);
      return;
    }

    try {
      // Проверяем существование обоих пользователей
      const checks = await Promise.all(
        referrals.map(contact => {
          const identifier = contact.includes('@') ? { email: contact } : { phone: contact };
          return apiClient.checkUserExists(identifier);
        })
      );

      if (!checks.every(result => result.exists)) {
        setMessage({ type: 'error', text: 'Один или оба указанных пользователя не найдены в системе. Пожалуйста, проверьте данные.' });
        setSubmitting(false);
        return;
      }

      // Если оба пользователя существуют, выдаем PRO-статус
      if (user) {
        await apiClient.grantPro(user.id);
        await refreshProfile(); // Обновляем профиль пользователя
        setMessage({ type: 'success', text: 'Поздравляем! Вам выдан PRO-статус. Обновите страницу, чтобы увидеть изменения.' });
        setReferrals(['', '']);
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Произошла ошибка. Попробуйте позже.' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleFeedbackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null); // Сбрасываем предыдущие сообщения
    setSubmitting(true);
    
    if (!feedbackForm.message.trim()) {
      setMessage({ type: 'error', text: 'Пожалуйста, напишите ваше сообщение.' });
      setSubmitting(false);
      return;
    }

    try {
      console.log('Начинаем отправку обратной связи...');
      console.log('Метод:', feedbackMethod);
      console.log('Данные формы:', feedbackForm);
      console.log('Пользователь:', user);
      
      if (feedbackMethod === 'site') {
        // Отправка через сайт - загружаем данные на сервер, бот автоматически отправляет в Telegram
        const feedbackData = {
          type: feedbackForm.type,
          message: feedbackForm.message,
          user_id: user?.id?.toString() || '',
          user_email: user?.email || '',
          image: feedbackForm.image
        };

        console.log('Подготавливаем данные для отправки:', feedbackData);

        // Отправляем данные на сервер, бот автоматически перешлет в Telegram
        console.log('Вызываем apiClient.sendFeedback...');
        await apiClient.sendFeedback(feedbackData);
        console.log('apiClient.sendFeedback выполнен успешно');
        
        // Увеличиваем счетчик отправленных сообщений
        const newCount = feedbackCount + 1;
        setFeedbackCount(newCount);

        if (newCount >= 2) {
          // Выдаем PRO-статус после отправки 2 сообщений
          if (user) {
            await apiClient.grantPro(user.id);
            await refreshProfile();
            setMessage({ type: 'success', text: 'Спасибо за обратную связь! Вам выдан PRO-статус. Обновите страницу, чтобы увидеть изменения.' });
            setFeedbackForm({ type: 'bug', message: '', image: null });
            setFeedbackCount(0); // Сбрасываем счетчик
          }
        } else {
          setMessage({ type: 'success', text: `Спасибо! Отправлено ${newCount} из 2 сообщений. Отправьте еще ${2 - newCount} сообщение для получения PRO-статуса.` });
          setFeedbackForm({ type: 'bug', message: '', image: null });
        }
      } else {
        // Отправка через бота - пользователь прикрепляет данные прямо в Telegram
        const feedbackText = `📝 Новая обратная связь от пользователя ${user?.email || user?.username || 'Неизвестный'}

Тип: ${feedbackForm.type === 'bug' ? '🐛 Ошибка' : '💡 Предложение'}
Сообщение: ${feedbackForm.message}

Пользователь: ${user?.email || user?.username || 'Неизвестный'}
ID: ${user?.id || 'Неизвестный'}
Страница: ${window.location.href}
Время: ${new Date().toLocaleString('ru-RU')}
Способ: Прямо в Telegram боте`;

        // Отправляем в Telegram через бота
        const telegramUrl = `https://t.me/myhpibot?start=feedback_${encodeURIComponent(feedbackText)}`;
        window.open(telegramUrl, '_blank');

        // Увеличиваем счетчик отправленных сообщений
        const newCount = feedbackCount + 1;
        setFeedbackCount(newCount);

        if (newCount >= 2) {
          // Выдаем PRO-статус после отправки 2 сообщений
          if (user) {
            await apiClient.grantPro(user.id);
            await refreshProfile();
            setMessage({ type: 'success', text: 'Спасибо за обратную связь! Вам выдан PRO-статус. Обновите страницу, чтобы увидеть изменения.' });
            setFeedbackForm({ type: 'bug', message: '', image: null });
            setFeedbackCount(0); // Сбрасываем счетчик
          }
        } else {
          setMessage({ type: 'success', text: `Спасибо! Отправлено ${newCount} из 2 сообщений. Отправьте еще ${2 - newCount} сообщение для получения PRO-статуса.` });
          setFeedbackForm({ type: 'bug', message: '', image: null });
        }
      }
    } catch (error) {
      console.error('Ошибка в handleFeedbackSubmit:', error);
      const errorMessage = error instanceof Error ? error.message : 'Неизвестная ошибка';
      console.error('Детали ошибки:', {
        name: error instanceof Error ? error.name : 'Unknown',
        message: errorMessage,
        stack: error instanceof Error ? error.stack : 'No stack'
      });
      setMessage({ type: 'error', text: `Произошла ошибка при отправке: ${errorMessage}` });
    } finally {
      setSubmitting(false);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFeedbackForm({ ...feedbackForm, image: file });
    }
  };

  const renderSelectedOption = () => {
    switch (selectedOption) {
      case 'referrals':
        return (
          <div className={styles.optionCard}>
            <h2 className={styles.optionTitle}>1. Указать приглашенных людей</h2>
            <p className={styles.optionDescription}>
              Укажите почту или телефон двух ваших знакомых, которые уже зарегистрированы в сервисе.
            </p>
            <form onSubmit={handleReferralSubmit}>
              <input
                type="text"
                placeholder="Почта или телефон первого человека"
                className={styles.input}
                value={referrals[0]}
                onChange={e => handleReferralChange(0, e.target.value)}
              />
              <input
                type="text"
                placeholder="Почта или телефон второго человека"
                className={styles.input}
                value={referrals[1]}
                onChange={e => handleReferralChange(1, e.target.value)}
              />
              <button type="submit" className={styles.button} disabled={submitting}>
                {submitting ? 'Проверяем...' : 'Отправить'}
              </button>
            </form>
          </div>
        );
      case 'share':
        return (
          <div className={styles.optionCard}>
            <h2 className={styles.optionTitle}>2. Поделиться результатом в чате телеграмм</h2>
            <p className={styles.optionDescription}>
              Нажмите кнопку ниже, чтобы получить ваш дашборд в Telegram. Затем перешлите его в наш канал для получения PRO-статуса.
            </p>
            <a 
              href={`https://t.me/myhpibot?start=${shareUtm}`} 
              target="_blank" 
              rel="noopener noreferrer" 
              className={styles.button}
              onClick={() => console.log(`Открывается ссылка с UTM: ${shareUtm}`)}
            >
              Получить дашборд в Telegram
            </a>
          </div>
        );
      case 'feedback':
        if (feedbackMethod === null) {
          return (
            <div className={styles.optionCard}>
              <h2 className={styles.optionTitle}>3. Отправить недоработку или пожелания</h2>
              <p className={styles.optionDescription}>
                Выберите способ отправки обратной связи:
              </p>
              <div className={styles.feedbackMethods}>
                <div 
                  className={`${styles.methodCard} ${styles.choiceCard}`} 
                  onClick={() => { setFeedbackMethod('site'); setMessage(null); }}
                >
                  <h3>Прямо на сайте</h3>
                  <p>Загрузите фото и текст, бот автоматически отправит в Telegram</p>
                </div>
                <div 
                  className={`${styles.methodCard} ${styles.choiceCard}`} 
                  onClick={() => { setFeedbackMethod('bot'); setMessage(null); }}
                >
                  <h3>Через бота</h3>
                  <p>Прикрепите фото и текст прямо в Telegram боте</p>
                </div>
              </div>
              <button onClick={() => { setSelectedOption(null); setMessage(null); }} className={styles.backButton}>
                &larr; Назад к выбору
              </button>
            </div>
          );
        }

        return (
          <div className={styles.optionCard}>
            <h2 className={styles.optionTitle}>
              3. Отправить недоработку или пожелания
              {feedbackMethod === 'site' && ' (прямо на сайте)'}
              {feedbackMethod === 'bot' && ' (через бота)'}
            </h2>
            <p className={styles.optionDescription}>
              {feedbackMethod === 'bot' 
                ? `Помогите нам стать лучше. Прикрепите фото и текст прямо в Telegram боте. Отправлено: ${feedbackCount}/2`
                : `Помогите нам стать лучше. Загрузите фото и текст, бот автоматически отправит данные в Telegram. Отправлено: ${feedbackCount}/2`
              }
            </p>
            <form onSubmit={handleFeedbackSubmit}>
              <div className={styles.feedbackType}>
                <label>
                  <input
                    type="radio"
                    name="feedbackType"
                    value="bug"
                    checked={feedbackForm.type === 'bug'}
                    onChange={(e) => setFeedbackForm({ ...feedbackForm, type: e.target.value })}
                  />
                  Ошибка
                </label>
                <label>
                  <input
                    type="radio"
                    name="feedbackType"
                    value="feature"
                    checked={feedbackForm.type === 'feature'}
                    onChange={(e) => setFeedbackForm({ ...feedbackForm, type: e.target.value })}
                  />
                  Предложение
                </label>
              </div>
              <textarea
                placeholder="Опишите проблему или ваше предложение..."
                className={styles.textarea}
                value={feedbackForm.message}
                onChange={(e) => setFeedbackForm({ ...feedbackForm, message: e.target.value })}
                rows={4}
                required
              />
              {feedbackMethod === 'site' && (
                <div className={styles.imageUpload}>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    style={{ display: 'none' }}
                  />
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className={styles.imageButton}
                  >
                    {feedbackForm.image ? 'Фото выбрано' : 'Прикрепить фото'}
                  </button>
                  {feedbackForm.image && (
                    <p className={styles.imageName}>{feedbackForm.image.name}</p>
                  )}
                </div>
              )}
              <button type="submit" className={styles.button} disabled={submitting}>
                {submitting ? 'Отправляем...' : 
                  feedbackMethod === 'site' ? 'Отправить на сайт' : 'Открыть Telegram бота'
                }
              </button>
            </form>
            <button 
              onClick={() => { setFeedbackMethod(null); setMessage(null); setFeedbackForm({ type: 'bug', message: '', image: null }); }} 
              className={styles.backButton}
            >
              &larr; Назад к выбору способа
            </button>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Получить PRO-статус</h1>
      <p className={styles.subtitle}>
        Вы можете получить PRO-статус бесплатно, выполнив одно из следующих действий:
      </p>

      {message && (
        <div className={`${styles.message} ${message.type === 'success' ? styles.success : styles.error}`}>
          {message.text}
        </div>
      )}

      {selectedOption ? (
        <div>
          {renderSelectedOption()}
        </div>
      ) : (
        <div className={styles.optionsGrid}>
          <div className={`${styles.optionCard} ${styles.choiceCard}`} onClick={() => setSelectedOption('referrals')}>
            <h2 className={styles.optionTitle}>1. Указать приглашенных людей</h2>
            <p className={styles.optionDescription}>Пригласите двух зарегистрированных пользователей.</p>
          </div>
          <div className={`${styles.optionCard} ${styles.choiceCard}`} onClick={() => setSelectedOption('share')}>
            <h2 className={styles.optionTitle}>2. Поделиться результатом в чате телеграмм</h2>
            <p className={styles.optionDescription}>Расскажите о своих успехах в нашем сообществе.</p>
          </div>
          <div className={`${styles.optionCard} ${styles.choiceCard}`} onClick={() => setSelectedOption('feedback')}>
            <h2 className={styles.optionTitle}>3. Отправить недоработку или пожелания</h2>
            <p className={styles.optionDescription}>Помогите нам стать лучше.</p>
          </div>
        </div>
      )}
    </div>
  );
} 