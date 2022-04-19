<template>
    <div>
      <!-- 面包屑导航 -->
      <el-breadcrumb separator-class="el-icon-arrow-right">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>模块管理</el-breadcrumb-item>
      </el-breadcrumb>
      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="formInline" class="user-search">
        <el-form-item label="项目名称：">
          <el-autocomplete size="small" v-model="formInline.projectName" placeholder="输入项目名称" @select="handleSelect" :fetch-suggestions="querySearchAsync" @input="inputChange"></el-autocomplete>
        </el-form-item>
        <el-form-item label="项目环境名称：">
          <el-select size="small" v-model="e_value" clearable placeholder="请选择" @change="handleChange">
            <el-option
              v-for="item in e_options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button size="small" type="primary" icon="el-icon-search" @click="search">搜索</el-button>
        </el-form-item>
      </el-form>
      <!-- 主体内容 -->
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card class="box-card;">
            <el-input
              size="small"
              placeholder="输入关键字进行过滤"
              v-model="filterText">
            </el-input>
            <div style="margin: 20px;"></div>
            <el-tree
              class="filter-tree"
              :data="listData"
              :props="defaultProps"
              node-key="id"
              default-expand-all
              :highlight-current="true"
              :filter-node-method="filterNode"
              @node-click="handleNodeClick"
              ref="tree">
            </el-tree>
          </el-card>
        </el-col>
        <el-col :span="20">
          <el-card class="box-card;">
            <div class="mod-btnbox">
              <el-button size="small" type="primary" icon="el-icon-plus" @click="handleAdd">添加</el-button>
            </div>
            <el-form label-width="120px" :model="editForm" :rules="rules" ref="editForm">
              <el-form-item label="父模块" prop="parent_m_name">
                <el-select size="small" v-model="p_value1" clearable placeholder="请选择" @change="p_handleChange">
                  <el-option
                    v-for="item in p_options1"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                  </el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="模块名称" prop="m_name">
                <el-input size="small" v-model="editForm.m_name" auto-complete="off" placeholder="请输入模块名称"></el-input>
              </el-form-item>
              <el-form-item label="模块描述" prop="m_description">
                <el-input type="textarea" size="small" v-model="editForm.m_description" auto-complete="off" placeholder="请输入模块描述"></el-input>
              </el-form-item>
              <el-form-item>
                <el-button size="small" type="primary" @click="saveModule('editForm')">保存</el-button>
                <el-button size="small" type="primary" @click="projectModuleDelete">删除</el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
      <el-dialog title="添加" :visible.sync="addFormVisible" width="30%" @click="closeDialog">
        <el-form label-width="120px" :model="addForm" :rules="rules" ref="addForm">
          <el-form-item label="父模块" prop="parent_m_name">
            <el-select size="small" v-model="p_value2" clearable placeholder="请选择" @change="p_handleChange">
              <el-option
                v-for="item in p_options2"
                :key="item.value"
                :label="item.label"
                :value="item.value">
              </el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="模块名称" prop="m_name">
            <el-input size="small" v-model="addForm.m_name" auto-complete="off" placeholder="请输入模块名称"></el-input>
          </el-form-item>
          <el-form-item label="模块描述" prop="m_description">
            <el-input type="textarea" size="small" v-model="addForm.m_description" auto-complete="off" placeholder="请输入模块描述"></el-input>
          </el-form-item>
          <el-form-item>
            <el-button size="small" type="primary" @click="saveModule('addForm')">保存</el-button>
            <el-button size="small" type="primary" @click="closeDialog">取消</el-button>
          </el-form-item>
        </el-form>
      </el-dialog>
    </div>
</template>

<script>
import { getAllProject, projectModuleList, addProjectModule, editProjectModule, deleteProjectModule, getAllProjectEnvironment } from '../../api/projectApi'
import { list_to_option, list_to_tree } from '../../utils/util'
export default {
  data() {
    return {
      formInline: {
        varLable: '',
        varName: '',
        projectName:'',
        projectEnvironment_id: '',
        projectEnvironment_name: '',
      },
      // rules表单验证
      rules: {
        m_name: [{ required: true, message: '请输入模塊名称', trigger: 'blur' }],
        m_description: [{ required: true, message: '请输入模塊描述', trigger: 'blur' }]
      },
      editForm: {
        id: '',
        e_id: '',
        e_name: '',
        parent_id: '',
        m_name: '',
        m_description: '',
      },
      addForm: {
        e_id: '',
        e_name: '',
        parent_id: '',
        m_name: '',
        m_description: '',
      },
      // 项目环境下拉框选项
      e_options: '',
      e_value: '',
      // 编辑页父模块下拉框选项
      p_options1: '',
      p_value1: '',
      // 添加页父模块下拉框选项
      p_options2: '',
      p_value2: '',
      addFormVisible: false,
      projects: '',
      filterText: '',
      originData: [],
      listData: [],
      defaultProps: {
        children: 'children',
        label: 'module_name'
      }
    }
  },
  created() {
    this.loadAllProject();
  },
  watch: {
    filterText(val) {
      this.$refs.tree.filter(val);
    }
  },
  methods: {
    // 获取数据
    getdata(parameter) {
      parameter = {
        projectEnvironment_id : this.formInline.projectEnvironment_id
      };
      projectModuleList(parameter)
        .then(res => {
          if (res.success === false) {
            this.$message({
              type: 'info',
              message: res.msg
            })
          } else {
            this.originData = res.data;
            if (this.originData.length > 0) {
              this.p_options1 = list_to_option(this.originData);
              this.p_options2 = this.p_options1;
              this.listData = list_to_tree(this.originData);
            } else {
              this.p_options1 = '';
              this.p_options2 = '';
              this.listData = [];
            }
            this.editForm.e_id = this.formInline.projectEnvironment_id;
          }
        })
        .catch(err => {
          this.loading = false;
          console.log(err);
          this.$message.error('菜单加载失败，请稍后再试！')
        })
    },
    // 搜索事件
    search() {
      this.getdata(this.formInline)
    },
    filterNode(value, data) {
      if (!value) return true;
      return data.module_name.indexOf(value) !== -1;
    },
    handleNodeClick(data) {
      this.editForm.id = data.id;
      this.editForm.parent_id = data.parent_id;
      this.p_value1 = data.parent_id !== 0 ? data.parent_id : '';
      this.p_value2 = data.id !== 0 ? data.id : '';
      this.editForm.m_name = data.module_name;
      this.editForm.m_description = data.module_description;
    },
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
          this.e_options = res;
        }
      )
    },
    // 选择项目环境名称后，获取api模块列表
    handleChange(val){
      this.formInline.projectEnvironment_id = val;
      let obj = {};
      obj = this.e_options.find((item) => {
        return item.value === val;
      });
      if(obj !== undefined){
        this.formInline.projectEnvironment_name = obj.label;
      }
      this.getdata(this.formInline);
    },
    p_handleChange(val) {
      this.editForm.parent_id = val;
    },
    //項目名稱修改后清空環境選擇
    inputChange(){
      this.formInline.projectEnvironment_id = '';
      this.formInline.projectEnvironment_name = '';
      this.e_options = '';
      this.e_value = '';
    },
    // 将后端返回模块数据转成下拉选项option
    list_to_option(data){
      let list = [];
      for (let i = 0; i < data.length; i++){
        let row = data[i];
        list.push({'label': row.module_name, 'value': row.id});
      }
      return list;
    },
    // 编辑、增加页面保存方法
    saveModule(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          let param;
          if (form === 'addForm') {
            param = this.addForm;
            addProjectModule(param)
            .then(res => {
              this.addFormVisible = false;
              this.loading = false;
              if (res.success) {
                this.getdata(this.formInline);
                this.$message({
                  type: 'success',
                  message: res.msg
                })
              } else {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              }
            })
            .catch(err => {
              this.editFormVisible = false;
              this.loading = false;
              this.$message.error('模块保存失败，请稍后再试！')
            })
          } else if (form === 'editForm') {
            param = this.editForm;
            editProjectModule(param)
            .then(res => {
              this.addFormVisible = false;
              this.loading = false;
              if (res.success) {
                this.getdata(this.formInline);
                this.$message({
                  type: 'success',
                  message: res.msg
                })
              } else {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              }
            })
            .catch(err => {
              this.editFormVisible = false;
              this.loading = false;
              this.$message.error('模块保存失败，请稍后再试！')
            })
          }
        } else {
          return false
        }
      })
    },
    // 打开添加框
    handleAdd() {
      this.addFormVisible = true;
      this.addForm.e_id = this.formInline.projectEnvironment_id;
      this.addForm.m_name = '';
      this.addForm.m_description = '';
      this.addForm.parent_id = this.p_value2;
    },
    // 关闭编辑、增加弹出框
    closeDialog() {
      this.addFormVisible = false;
    },
    // 删除模块
    projectModuleDelete() {
      this.$confirm('确定要删除吗?', '信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          let parameter = {
            id: this.editForm.id
          };
          deleteProjectModule(parameter)
            .then(res => {
              if (res.success) {
                this.$message({
                  type: 'success',
                  message: res.msg
                });
                this.getdata(this.formInline);
                this.editForm.id = '';
                this.editForm.parent_id = '';
                this.editForm.m_name = '';
                this.editForm.m_description = '';
              } else {
                this.$message({
                  type: 'info',
                  message: res.msg
                })
              }
            })
            .catch(err => {
              console.log(err);
              this.loading = false;
              this.$message.error('模块删除失败，请稍后再试！')
            })
        })
        .catch((err) => {
          console.log(err)
        })
    }
  }
}
</script>

<style scoped>
/deep/ textarea {
  font-family: "Helvetica Neue",Helvetica,"PingFang SC","Hiragino Sans GB","Microsoft YaHei","微软雅黑",Arial,sans-serif !important;
}
.treeclass {
  border: 1px solid #f3f3f3;
  padding-top: 20px;
  padding-bottom: 20px;
}
</style>
