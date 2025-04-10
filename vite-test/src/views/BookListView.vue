<script lang="ts" setup>
const tableData = [
    {
        isbn: "9787512666931",
        title: "边城[专著]",
        author: "沈从文(1902~1988) 著",
        translator: "",
        genre: "长篇小说",
        country: "中国",
        era: "现代",
        opac_nlc_class: "I246.57",
        publisher: "团结出版社",
        publish_year: "2019",
        page: "236",
        cover_url: "",
        description: "",
    },
]
</script>


<template>
    <div class="example-pagination-block">
        <div class="example-demonstration">
            <el-table :data="tableData" height="250" style="width: 100%">
                <el-table-column prop="isbn" label="ISBN" width="180" />
                <el-table-column prop="title" label="Title" width="180" />
                <el-table-column prop="author" label="Author" width="180" />
                <el-table-column prop="translator" label="Translator" width="180" />
                <el-table-column prop="genre" label="Genre" width="180" />
                <el-table-column prop="country" Label="Country" width="180" />
                <el-table-column prop="era" label="Era" width="180" />
                <el-table-column prop="opac_nlc_class" label="中图分类号" width="180" />
                <el-table-column prop="publisher" label="Publisher" width="180" />
                <el-table-column prop="publish_year" label="Publish Year" width="180" />
                <el-table-column prop="page" label="Page" width="180" />
                <el-table-column prop="cover_url" label="封面链接" width="180" />
                <el-table-column prop="description" label="Description" width="180" />
            </el-table>
        </div>
        <el-pagination layout="prev, pager, next" :total="1000" />
    </div>
</template>

<style scoped>
.example-pagination-block+.example-pagination-block {
    margin-top: 10px;
}

.example-pagination-block .example-demonstration {
    margin-bottom: 16px;
}
</style>