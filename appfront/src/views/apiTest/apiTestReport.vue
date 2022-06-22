<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/apiTest/apiTestTask' }">测试任务</el-breadcrumb-item>
      <el-breadcrumb-item>测试用例</el-breadcrumb-item>
    </el-breadcrumb>
    <div style="margin: 20px;"></div>
    <div>
      <div style="font-size: 40px;font-family: Avenir,Helvetica,Arial,sans-serif;">{{report_title}}</div>
      <div style="font-family: Avenir,Helvetica,Arial,sans-serif;">测试结果：总共 {{all_count}}，通过{{pass_count}}，失败{{fail_count}}，通过率= {{parseFloat((pass_count/all_count)*100).toFixed(2)}}</div>
    </div>
    <div style="margin: 20px;"></div>
    <!-- 表格报告 -->
    <el-table size="small" :data="listData" v-loading="loading" border element-loading-text="拼命加载中" style="width: 100%;"
              :header-cell-style="{background:'#eef1f6',color:'#606266'}" :row-style="tableRowStyle2">
      <el-table-column type="expand">
        <template slot-scope="scope">
          <el-table :data="scope.row.testcase" style="width: calc(100% - 47px)" size="small" border
                    :header-cell-style="{background:'#eef1f6'}" :row-style="tableRowStyle1" :show-header="false">
            <el-table-column sortable prop="testcase_name" label="用例名称">
            </el-table-column>
            <el-table-column sortable prop="status" label="状态">
              <template scope="scope">
                <el-tag type="success" v-if="scope.row.status===1">通过</el-tag>
                <el-tag type="danger" v-if="scope.row.status===2">失败</el-tag>
              </template>
            </el-table-column>
            <el-table-column align="center" label="操作" width="300">
              <template slot-scope="scope">
                <el-button size="mini" @click="checkLog(scope.row)">日志</el-button>
              </template>
            </el-table-column>
          </el-table>
        </template>
      </el-table-column>
      <el-table-column sortable prop="api_name" label="api名称">
      </el-table-column>
      <el-table-column sortable prop="module_name" label="模块套件">
      </el-table-column>
      <el-table-column sortable prop="all_count" label="总计" width="250">
      </el-table-column>
      <el-table-column sortable prop="pass_count" label="通过" width="250">
      </el-table-column>
      <el-table-column sortable prop="fail_count" label="失败" width="250">
        <template slot-scope="scope">
          <div v-if="scope.row.fail_count > '0'">
            <div style="color: #EA1B29">{{scope.row.fail_count}}</div>
          </div>
          <div v-else>
            <div>{{scope.row.fail_count}}</div>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <!-- 日志弹框 -->
    <el-dialog :title="title" :visible.sync="logDialogVisible" width="65%">
      <el-card class="box-card;">
        <el-scrollbar style="height: 500px;overflow-wrap:break-word;">
          <div v-for="value in debugLog">
            <div v-if="typeof value === 'string'">
              <div v-if="value.includes('INFO')">
                <!--<span v-if="value.includes('{')">{{value.split(' : ')[0]+' : '}}{{jsonView(value)}}</span>-->
                <!--<span v-if="value.includes('{')">{{value.split(' : ')[0]+' : '+value.split(' : ')[1].split(':')[0]+':'}}<JsonView :json="jsonView(value)"></JsonView></span>-->
                <!--<span v-else>{{value}}</span>-->
                <span>{{value}}</span>
              </div>
              <div v-else-if="value.includes('ERROR')">
                <span style="color: red">{{value}}</span>
              </div>
            </div>
            <div v-else>
              <span><JsonView :json="value"></JsonView></span>
            </div>
          </div>
        </el-scrollbar>
      </el-card>
    </el-dialog>
  </div>

</template>

<script>
  import { apiTestReport } from '../../api/apiTestApi'
  import JsonView from '../../components/JsonView'
    export default {
      components: {JsonView},
      data() {
        return {
          task_id: '',
          listData: [],
          all_count: '',
          pass_count: '',
          fail_count: '',
          report_title: '',
          logDialogVisible: false,
          title: '日志',
          debugLog: []
        }
      },
      created() {
        this.getParams();
        this.getdata();
      },
      methods: {
        getParams(){
          // 取到路由带过来的参数
          this.task_id = this.$route.query.task_id;
        },
        getdata(parameter) {
          parameter = {
            task_id : this.task_id
          };
          apiTestReport(parameter)
            .then(res => {
              this.loading = false;
              if (res.success === false) {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              } else {
                this.listData = res.data;
                this.all_count = res.all_count;
                this.pass_count = res.pass_count;
                this.fail_count = res.fail_count;
                this.report_title = res.title;
                console.log(res.all_count);
              }
            })
            .catch(err => {
              this.loading = false;
              console.log(err);
              this.$message.error('菜单加载失败，请稍后再试！')
            })
        },
        // 查看日志
        checkLog(row){
          this.debugLog = row.output_log;
          this.logDialogVisible = true;
        },
        //切换json显示
        jsonView(str){
          let v = str.match(/\{.*\}/);
          try {
            // console.log(v[0]);
            // console.log(typeof jsonData);
            // console.log(jsonData);
            return JSON.parse(v[0]);
          } catch (e) {
            console.log(e);
            return str
          }
        },
        // 动态修改内表格行背景色
        tableRowStyle1({ row, rowIndex }) {
          // 注意，这里返回的是一个对象
          let rowBackground = {};
          if (row.status === 1 ) {
            rowBackground.background = "#a8c2a6";
          } else {
            rowBackground.background = "#f5c1bf";
          }
          return rowBackground;
        },
        tableRowStyle2({row, rowIndex}){
          let rowBackground = {};
          if (row.fail_count > 0){
            rowBackground.background = "#f5c1bf";
          }
          return rowBackground;
        }
      }
    }
</script>

<style scoped>

</style>
