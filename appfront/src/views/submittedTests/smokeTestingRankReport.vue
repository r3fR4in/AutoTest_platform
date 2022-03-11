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
    <!-- 图形 -->
    <div id="echarts_box" style="width: 90%;height: 400px"></div>
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
import echarts from 'echarts'
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
              this.showChart(res.data);
            }
          })
          .catch(err => {
            this.loading = false;
            console.log(err);
            this.$message.error('报表加载失败，请稍后再试！')
          })
    },
    // echarts渲染
    showChart(data) {
      let myChart = echarts.init(document.getElementById('echarts_box'));
      let option = {
        legend: {},
        tooltip: {},
        dataset: {
          source: [
            ['items', '通过率', '提测总数', '通过数']  // 图例
          ]
        },
        xAxis: { type: 'category' },
        yAxis: [
          {
            name: '通过率%',
            type: 'value',
            min: 0,
            max: 100
          },
          {
            name: '数量',
            type: 'value',
            min: 0,
            max: 100
          }
        ],
        series: [{
          type: 'bar',
          yAxisIndex: 0
        }, {
          type: 'bar',
          yAxisIndex: 1
        }, {
          type: 'bar',
          yAxisIndex: 1
        }]
      };
      // 遍历data，将数据加入source中
      let max_num = 0; //设置最大值，用于动态设置数量y轴最大值
      data.forEach(item => {
        let array = [item.projectName + '-' + item.submitted_test_director, item.smokeTesting_pass_rate, item.submittedTest_num, item.smokeTesting_pass_num];
        option.dataset.source.push(array);
        if (item.submittedTest_num > max_num){
          max_num = item.submittedTest_num;
        }
      });
      let max_num_re = max_num % 5;
      max_num = max_num + (5 - max_num_re);
      option.yAxis[1].max = max_num;
      myChart.setOption(option);
    }
  }
}
</script>

<style scoped>

</style>
