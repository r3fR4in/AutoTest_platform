/**
* 头部菜单
*/
<template>
  <el-menu class="el-menu-demo" mode="horizontal" background-color="#334157" text-color="#fff" active-text-color="#fff">
    <el-button class="buttonimg">
      <img class="showimg" :src="collapsed?imgsq:imgshow" @click="toggle(collapsed)">
    </el-button>
    <div style="float: right">
      <div style="display:inline">
        <el-badge style="margin-top: 9px;margin-right: 9px;border: none" :is-dot="dot">
          <el-button index="2" icon="el-icon-bell" circle style="border: none;font-size: 17px" type="primary" @click="openDrawer(true)"></el-button>
        </el-badge>
      </div>
      <el-submenu index="3" class="submenu">
        <!-- <template slot="title">{{user.userRealName}}</template> -->
        <template slot="title">{{user.nickname}}</template>
        <!--<el-menu-item index="2-1">设置</el-menu-item>-->
        <el-menu-item @click="toModifyPwd" index="2-2">修改密碼</el-menu-item>
        <el-menu-item @click="exit()" index="2-3">退出</el-menu-item>
      </el-submenu>
    </div>
    <el-drawer
      title="消息"
      :visible.sync="drawer"
      direction="rtl"
      @closed="handleClose">
      <!--<div style="width: 90%;height: 100%;display: block">-->
      <!--<el-scrollbar wrap-style="overflow-x:auto;" style="height: 100%;overflow-wrap:break-word;">-->
      <el-timeline style="width: 90%">
        <el-timeline-item
          v-for="item in listData"
          placement="top"
          :timestamp="item.create_time">
          <el-badge style="display: block" :is-dot="item.is_read === 0">
            <el-card>
              <h4>{{item.title}}</h4>
              <p>{{item.content}}</p>
            </el-card>
          </el-badge>
        </el-timeline-item>
      </el-timeline>
      <!--</el-scrollbar>-->
      <!--</div>-->
    </el-drawer>
  </el-menu>
</template>
<script>
import { logout } from '../api/userMG'
import { getMessage, clearUnreadMessage, pushMessage } from '../api/messageApi'
export default {
  name: 'navcon',
  data() {
    return {
      collapsed: true,
      imgshow: require('../assets/img/show.png'),
      imgsq: require('../assets/img/sq.png'),
      drawer: false,
      listData: '',
      dot: false,
      user: {},
      notifyPromise: Promise.resolve()
    }
  },
  // 创建完毕状态(里面是操作)
  created() {
    this.user = JSON.parse(localStorage.getItem('userdata'));
    this.openDrawer(false);
    this.pushMessage();
    setInterval(() => {
      setTimeout(() => {
        this.pushMessage();
      }, 0);
    }, 5*60000);
  },
  methods: {
    // 跳转修改密码页面
    toModifyPwd(row){
      // // 将搜索条件存入cookie
      this.$router.push({
        path: '/system/modifyPwd',
      })
    },
    // 退出登录
    exit() {
      this.$confirm('退出登录, 是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
        .then(() => {
          // setTimeout(() => {
          //   this.$store.commit('logout', 'false');
          //   this.$router.push({ path: '/login' });
          //   this.$message({
          //     type: 'success',
          //     message: '已退出登录!'
          //   })
          // }, 1000);
          logout()
            .then(res => {
              if (res.success) {
                //如果请求成功就让他2秒跳转路由
                setTimeout(() => {
                  this.$store.commit('logout', 'false');
                  this.$router.push({ path: '/login' });
                  localStorage.removeItem('userInfo');
                  localStorage.removeItem('logintoken');
                  localStorage.removeItem('userdata');
                  localStorage.removeItem('menu');
                  this.$message({
                    type: 'success',
                    message: '已退出登录!'
                  })
                }, 1000)
              } else {
                this.$message.error(res.msg);
                this.logining = false;
                return false
              }
            })
            .catch(err => {
              this.logining = false;
              this.$message.error('退出失败，请稍后再试！')
            })
        })
        .catch(() => {
          this.$message({
            type: 'info',
            message: '已取消'
          })
        })
    },
    // 切换显示
    toggle(showtype) {
      this.collapsed = !showtype;
      this.$root.Bus.$emit('toggle', this.collapsed)
    },
    // 打开消息抽屉
    openDrawer(bool){
      this.drawer = bool;
      getMessage().then(res => {
        if (res.success === false) {
          this.$message({
            type: 'info',
            message: res.msg
          })
        } else {
          this.listData = res.data;
          this.dot = res.unread_count > 0;
        }
      })
    },
    // 关闭消息抽屉后清空未读提示
    handleClose(){
      clearUnreadMessage().then(res => {
        if (res.success === false) {
          this.$message({
            type: 'info',
            message: res.msg
          })
        } else {
          this.dot = false;
        }
      })
    },
    // 获取未推送消息
    pushMessage(){
      pushMessage().then(res => {
        res.forEach((item) => {
          this.notifyPromise = this.notifyPromise.then(() => {
            this.$notify({
              title: item.title,
              message: item.content,
              duration: 0
            });
          });
        });
      })
      .catch(err => {
        console.log(err);
      });
    }
  }
}
</script>
<style scoped>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  border: none;
}
.el-button{
  background-color: #334157;
}
.el-button:hover{
  background-color: #293446;
}
.submenu {
  float: right;
  display: inline;
}
.buttonimg {
  height: 60px;
  background-color: transparent;
  border: none;
}
.showimg {
  width: 26px;
  height: 26px;
  position: absolute;
  top: 17px;
  left: 17px;
}
.showimg:active {
  border: none;
}
</style>
<style>
.el-drawer__body {
  overflow: auto;
  /* overflow-x: auto; */
}
.el-drawer__container ::-webkit-scrollbar{
    display: none;
}
</style>
