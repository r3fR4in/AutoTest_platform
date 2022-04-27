<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>项目非一次性通过原因分析</el-breadcrumb-item>
    </el-breadcrumb>
    <div style="margin: 20px;"></div>
    <!-- 搜索筛选 -->
    <el-form :inline="true" :model="formInline" class="user-search">
      <el-form-item label="查询时间：">
        <el-date-picker
          v-model="date"
          size="small"
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
    <div v-for="(value,key,index) in list[0]" ref="list">
      <div style="font-size: 20px;font-family: Avenir,Helvetica,Arial,sans-serif;">{{value[0]['projectName']}}</div>
      <el-table size="small" :data="value" highlight-current-row v-loading="loading" :span-method="objectSpanMethod" border element-loading-text="拼命加载中" style="width: 100%;">
        <el-table-column prop="project_id" label="项目id" v-if=false>
        </el-table-column>
        <el-table-column sortable prop="smoke_testing_fail_reason_category" label="原因分类" min-width="150">
        </el-table-column>
        <el-table-column sortable prop="smoke_testing_fail_reason_detail" label="原因分析" min-width="150">
        </el-table-column>
        <el-table-column sortable prop="smoke_testing_fail_reason_detail_num" label="出现次数" min-width="150">
        </el-table-column>
        <el-table-column sortable prop="detail_rate" label="占比" min-width="150">
        </el-table-column>
        <el-table-column sortable prop="category_rate" label="总占比" min-width="150">
        </el-table-column>
      </el-table>
      <div style="margin-top: 20px;">
    </div>
  </div>
</template>

<script>
import { smokeTestingFailReasonAnalysisReport } from '../../api/submittedTestsApi'
export default {
  data() {
    return {
      date: '',
      list: '',
      categoryArr:[], //第一列做合并操作时存放的数组变量
      categoryPos: 0  //上面数组的下标值
    }
  },
  methods: {
    // 搜索事件
    search() {
      let param = {
        start_date: this.date[0],
        end_date: this.date[1]
      };
      smokeTestingFailReasonAnalysisReport(param)
        .then(res => {
            this.loading = false;
            if (res.success === false) {
              this.$message({
                type: 'info',
                message: res.msg
              })
            } else {
              this.list = res.data;
            }
          })
          .catch(err => {
            this.loading = false;
            console.log(err);
            this.$message.error('报表加载失败，请稍后再试！')
          })
    },
    // merageInit() {
    //     this.categoryArr = [];
    //     this.categoryPos = 0;
    // },
    // merage(index) {
    //   this.merageInit();
    //   console.log(this.$refs.list);
    //   for (let i = 0; i < this.$refs.list[index].length; i += 1) {
    //     if (i === 0){
    //       // 第一行必须存在
    //       this.categoryArr.push(1);
    //       this.categoryPos = 0;
    //     } else {
    //       // 判断当前元素与上一个元素是否相同,eg：this.categoryPos 是 this.categoryArr
    //       // 第一列 下面的是eslint的不限制语法
    //       // eslint-disable-next-line no-lonely-if
    //       if (this.$refs.list[index][i].smoke_testing_fail_reason_category === this.$refs.list[index][i - 1].smoke_testing_fail_reason_category) {
    //         this.categoryArr[this.categoryPos] += 1;
    //         this.categoryArr.push(0);
    //       } else {
    //         this.categoryArr.push(1);
    //         this.categoryPos = i;
    //       }
    //     }
    //   }
    // },
    // objectSpanMethod({ row, column, rowIndex, columnIndex }) {
    //   if (columnIndex === 0) {
    //     // 第一列的合并方法
    //     const row1 = this.categoryArr[rowIndex];
    //     return {
    //       rowspan: row1,
    //       colspan: 1
    //     };
    //   } else if (columnIndex === 3){
    //     const row1 = this.categoryArr[rowIndex];
    //     return {
    //       rowspan: row1,
    //       colspan: 1
    //     };
    //   } else {
    //     return {
    //       rowspan: 0,
    //       colspan: 0
    //     };
    //   }
    // }
  }
}
</script>

<style scoped>

</style>
