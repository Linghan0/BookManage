<script lang="ts" setup>
import { reactive, ref } from 'vue'



const options = [
    {
        value: 'isbn',
        label: 'ISBN'
    },
    {
        value: 'title',
        label: '书名',
    },
    {    value: 'author',
        label: '作者',
    },
]

const formInline = reactive({
    msg: '',
    option: '',
})

const onSubmit = () => {
    console.log('submit!')
}
</script>


<template>
    <el-form :inline="true" :model="formInline" class="demo-form-inline">
        <el-form-item label="输入">
            <el-input v-model="formInline.msg" placeholder="" clearable />
        </el-form-item>
        <el-form-item label="搜索类型">
            <el-select v-model="formInline.option" placeholder="ISBN" clearable>
                <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
        </el-form-item>
        
        <el-form-item>
            <el-button type="primary" @click="onSubmit">搜索</el-button>
        </el-form-item>
    </el-form>
</template>

<style>
.demo-form-inline .el-input {
    --el-input-width: 220px;
}

.demo-form-inline .el-select {
    --el-select-width: 220px;
}
</style>