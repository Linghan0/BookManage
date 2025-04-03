<template>
  <div class="book-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <h1>{{ book.title }}</h1>
      <div class="book-info">
        <p><strong>作者:</strong> {{ book.author }}</p>
        <p><strong>ISBN:</strong> {{ book.isbn }}</p>
        <p><strong>出版社:</strong> {{ book.publisher }}</p>
        <p><strong>出版年份:</strong> {{ book.publish_year }}</p>
        <p><strong>页数:</strong> {{ book.page }}</p>
        <p><strong>分类:</strong> {{ book.genre }}</p>
        <p><strong>国家:</strong> {{ book.country }}</p>
        <p><strong>时代:</strong> {{ book.era }}</p>
        <p><strong>中图分类号:</strong> {{ book.opac_nlc_class }}</p>
      </div>
      <div class="book-description">
        <h3>内容简介</h3>
        <p>{{ book.description || '暂无简介' }}</p>
      </div>
      <button @click="goBack" class="back-button">返回列表</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BookDetail',
  data () {
    return {
      book: {},
      loading: false,
      error: null
    }
  },
  created () {
    this.fetchBookData()
  },
  methods: {
    async fetchBookData () {
      this.loading = true
      this.error = null
      try {
        const response = await fetch(`http://localhost:5000/api/books/${this.$route.params.isbn}`)
        if (!response.ok) throw new Error('图书不存在')
        this.book = await response.json()
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },
    goBack () {
      this.$router.push('/books')
    }
  }
}
</script>

<style scoped>
.book-detail {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
.loading, .error {
  text-align: center;
  padding: 20px;
  font-size: 18px;
}
.error {
  color: #ff5252;
}
.book-info {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 5px;
  margin: 20px 0;
}
.book-info p {
  margin: 8px 0;
}
.book-description {
  margin: 30px 0;
  line-height: 1.6;
}
.back-button {
  background-color: #42b983;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}
.back-button:hover {
  background-color: #369f6d;
}
</style>
