<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <h1>⏱️ Учёт времени </h1>
        <p>Эффективно отслеживайте время ваших проектов</p>
      </div>
    </header>
    <main class="app-main">
      <div class="container">
        <router-view />
      </div>
    </main>
    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 Учёт времени</p>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f8f9fa;
  font-size: 16px;
  /* Увеличиваем базовый размер шрифта */
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.app-header {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  color: white;
  padding: 2rem 0;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.app-main {
  min-height: calc(100vh - 200px);
  padding: 2rem 0;
}

.app-footer {
  background-color: #343a40;
  color: white;
  text-align: center;
  padding: 1rem 0;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  font-size: 18px;
  /* Увеличиваем шрифт в кнопках */
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover {
  background-color: #1e7e34;
}

.btn-warning {
  background-color: #ffc107;
  color: #212529;
}

.btn-warning:hover {
  background-color: #e0a800;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-control {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 18px;
  /* Увеличиваем шрифт в полях ввода */
}

.form-control:focus {
  border-color: #80bdff;
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.timer-display {
  font-family: 'Courier New', monospace;
  font-size: 1.5rem;
  font-weight: bold;
  color: #343a40;
}

.task-active {
  border-left: 4px solid #28a745;
  background-color: #f8fff9;
}

/* Увеличиваем шрифт в текстовых областях */
textarea.form-control {
  font-size: 18px;
  min-height: 120px;
  /* Делаем текстовые области больше */
}
</style>