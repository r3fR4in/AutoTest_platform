<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>完成提测冒烟测试排名</el-breadcrumb-item>
    </el-breadcrumb>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="formInline" class="user-search">
      <el-form-item label="查询时间：">
        <el-date-picker
          v-model="date"
          type="daterange"
          value-format="yyyy-MM-dd"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期">
        </el-date-picker>
      </el-form-item>
      <el-form-item>
        <el-button size="small" type="primary" icon="el-icon-search" @click="search">搜索</el-button>
      </el-form-item>
    </el-form>
    <!--列表-->
    <el-table size="small" :data="listData" highlight-current-row v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;">
      <el-table-column prop="project_id" label="项目id" v-if=false>
      </el-table-column>
      <el-table-column sortable prop="projectName" label="项目名称" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="submitted_test_director" label="提测负责人" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="submittedTest_num" label="提测总数" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="smokeTesting_pass_num" label="冒烟测试通过数" min-width="150">
      </el-table-column>
      <el-table-column sortable prop="smokeTesting_pass_rate" label="冒烟测试通过率" min-width="150">
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { smokeTestingRankReport } from '../../api/submittedTestsApi'
export default {
  data() {
    return {
      date: '',
      listData: ''
    }
  },
  methods: {
    // 搜索事件
    search() {
      let param = {
        start_date: this.date[0],
        end_date: this.date[1]
      };
      smokeTestingRankReport(param)
        .then(res => {
            this.loading = false;
            if (res.success === false) {
              this.$message({
                type: 'info',
                message: res.msg
              })
            } else {
              this.listData = res.data;
            }
          })
          .catch(err => {
            this.loading = false;
            console.log(err);
            this.$message.error('报表加载失败，请稍后再试！')
          })
    }
  }
}
</script>

<style scoped>

</style>
