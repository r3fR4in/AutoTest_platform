<template>
  <div>
    <!-- 面包屑导航 -->
    <el-breadcrumb separator-class="el-icon-arrow-right">
      <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
      <el-breadcrumb-item>接口导入</el-breadcrumb-item>
    </el-breadcrumb>
    <div style="margin-top: 20px;"></div>
    <!-- swagger导入 -->
    <el-card>
      <div slot="header" class="clearfix">
        <span>swagger导入</span>
      </div>
      <el-form :inline="true" :model="formInline" :rules="rules" class="user-search" ref="formInline">
        <el-form-item label="项目名称：" prop="projectName">
          <el-autocomplete size="small" v-model="formInline.projectName" placeholder="输入项目名称" @select="handleSelect" :fetch-suggestions="querySearchAsync" @input="inputChange"></el-autocomplete>
        </el-form-item>
        <el-form-item label="项目环境名称：" prop="projectEnvironment_name">
          <el-select size="small" v-model="formInline.projectEnvironment_name" clearable placeholder="请选择" @change="handleChange">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="url：" prop="url">
          <el-input size="small" v-model="formInline.url" placeholder="输入swagger url"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button size="small" type="primary" icon="el-icon-plus" @click="importFromSwagger('formInline')">导入</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { getAllProject, getAllProjectEnvironment } from '../../api/projectApi'
import { importFromSwagger } from '../../api/apiTestApi'
export default {
  data(){
    return {
      formInline: {
        varLable: '',
        varName: '',
        projectName:'',
        projectEnvironment_id: '',
        projectEnvironment_name: '',
        url: ''
      },
      // rules表单验证
      rules: {
        projectName: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
        projectEnvironment_name: [{ required: true, message: '请输入环境名称', trigger: 'blur' }],
        url: [{ required: true, message: '请输入url', trigger: 'blur' }]
      },
      // 下拉框选项
      options: '',
      value: ''
    }
  },
  created() {
    this.loadAllProject();
  },
  methods: {
    // 获取所有项目信息
    loadAllProject(){
      getAllProject().then(
        res => {
          this.projects = res;
        }
      )
    },
    querySearchAsync(queryString, cb) {
      var projects = this.projects;
      var results = queryString ? projects.filter(this.createStateFilter(queryString)) : projects;

      cb(results);
    },
    createStateFilter(queryString) {
      return (state) => {
        return (state.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0);
      };
    },
    handleSelect(item) {
      this.loadAllProjectEnvironment(item);
    },
    // 选择项目名称后，获取项目环境名称
    loadAllProjectEnvironment(item){
      var params = {
        name: item.value
      };
      getAllProjectEnvironment(params).then(
        res => {
          this.options = res;
        }
      )
    },
    handleChange(val){
      this.formInline.projectEnvironment_id = val;
      let obj = {};
      obj = this.options.find((item) => {
        return item.value === val;
      });
      if(obj !== undefined){
        this.formInline.projectEnvironment_name = obj.label;
      }
    },
    // 从swagger导入
    importFromSwagger(formInline){
      this.$refs[formInline].validate(valid => {
        if (valid) {
          let parameter = {
            'id': this.formInline.projectEnvironment_id,
            'url': this.formInline.url
          };
          importFromSwagger(parameter)
            .then(res => {
              this.loading = false;
              if (res.success === false) {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              } else {
                this.$message({
                  type: 'success',
                  message: res.msg
                })
              }
            })
            .catch(err => {
              this.loading = false;
              console.log(err);
              this.$message.error('导入失败，请稍后再试！')
            })
        } else {
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
.user-search {
  margin-top: 20px;
}
.userRole {
  width: 100%;
}
.clearfix:after {
  clear: both
}
/deep/ textarea {
  font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif !important;
}
</style>
