import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useNavigate, Link } from 'react-router-dom';

const SignupPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await register({ email, password, first_name: firstName, last_name: lastName });
      navigate('/account/profile');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h1>Регистрация</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Имя
          <input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
        </label>
        <label>
          Фамилия
          <input value={lastName} onChange={(e) => setLastName(e.target.value)} />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Пароль
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button type="submit" disabled={submitting}>{submitting ? 'Создаём…' : 'Зарегистрироваться'}</button>
      </form>
      <p>
        Уже есть аккаунт? <Link to="/login">Войти</Link>
      </p>
    </div>
  );
};

export default SignupPage; 