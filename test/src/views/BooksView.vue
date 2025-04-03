<template>
  <div class="books-view">
    <h1>图书管理系统</h1>
    <div class="book-list">
      <div v-for="book in books" :key="book.isbn" class="book-card">
        <h2>{{ book.title }}</h2>
        <p>作者: {{ book.author }}</p>
        <p v-if="book.translator">译者: {{ book.translator }}</p>
        <p>ISBN: {{ book.isbn }}</p>
        <p>出版社: {{ book.publisher }}</p>
        <p>出版年份: {{ book.publish_year }}</p>
        <p v-if="book.page">页数: {{ book.page }}</p>
        <p v-if="book.genre">分类: {{ book.genre }}</p>
        <p v-if="book.country">国家: {{ book.country }}</p>
        <p v-if="book.era">时代: {{ book.era }}</p>
        <p v-if="book.opac_nlc_class">中图分类号: {{ book.opac_nlc_class }}</p>
        <button @click="showDetails(book)">查看详情</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BooksView',
  data () {
    return {
      books: []
    }
  },
  created () {
    this.fetchBooks()
  },
  methods: {
    async fetchBooks () {
      try {
        const response = await fetch('http://localhost:5000/api/books')
        this.books = await response.json()
      } catch (error) {
        console.error('获取图书数据失败:', error)
      }
    },
    showDetails (book) {
      this.$router.push(`/books/${book.isbn}`)
    }
  }
}
</script>

<style scoped>
.books-view {
  padding: 20px;
}
.book-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}
.book-card {
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.book-card h2 {
  margin-top: 0;
  color: #333;
}
button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}
button:hover {
  background-color: #369f6d;
}
</style>
