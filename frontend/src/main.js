import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

// Vant UI
import 'vant/lib/index.css'
import {
  Button, Field, Form, Cell, CellGroup, NavBar, Tabbar, TabbarItem,
  Search, Card, Tag, Image, Grid, GridItem, Swipe, SwipeItem,
  PullRefresh, List, Tabs, Tab, Icon, Popup, Picker,
  Uploader, ActionSheet, Dialog, Notify, Toast, Loading,
  Empty, Divider, Badge, Sticky, Skeleton, DropdownMenu, DropdownItem,
  Collapse, CollapseItem, RadioGroup, Radio, Checkbox, Switch,
  ImagePreview, Overlay, ShareSheet, Step, Steps, Progress,
  Cascader, CheckboxGroup, CountDown, FloatingBubble, NoticeBar
} from 'vant'

const app = createApp(App)

// 全局注册 Vant 组件
const vantComponents = [
  Button, Field, Form, Cell, CellGroup, NavBar, Tabbar, TabbarItem,
  Search, Card, Tag, Image, Grid, GridItem, Swipe, SwipeItem,
  PullRefresh, List, Tabs, Tab, Icon, Popup, Picker,
  Uploader, ActionSheet, Dialog, Notify, Toast, Loading,
  Empty, Divider, Badge, Sticky, Skeleton, DropdownMenu, DropdownItem,
  Collapse, CollapseItem, RadioGroup, Radio, Checkbox, Switch,
  ImagePreview, Overlay, ShareSheet, Step, Steps, Progress,
  Cascader, CheckboxGroup, CountDown, FloatingBubble, NoticeBar
]
vantComponents.forEach(comp => app.component(comp.name || comp.__name, comp))

app.use(createPinia())
app.use(router)
app.mount('#app')
