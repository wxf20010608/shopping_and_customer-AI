import { createRouter, createWebHistory } from 'vue-router'
import ProductList from '@/views/products/ProductList.vue'
import CartView from '@/views/cart/CartView.vue'
import OrdersView from '@/views/orders/OrdersView.vue'
import ProductDetail from '@/views/products/ProductDetail.vue'
import OrderDetail from '@/views/orders/OrderDetail.vue'
import OrderLogistics from '@/views/orders/OrderLogistics.vue'
import WishlistView from '@/views/wishlist/WishlistView.vue'
import ProfileView from '@/views/profile/ProfileView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import RegisterView from '@/views/auth/RegisterView.vue'
import ProfileEditView from '@/views/profile/ProfileEditView.vue'
import AddressBookView from '@/views/profile/AddressBookView.vue'
import MembershipView from '@/views/profile/MembershipView.vue'
import MembershipDetailView from '@/views/profile/MembershipDetailView.vue'
import MembershipPurchaseView from '@/views/profile/MembershipPurchaseView.vue'
import AdminDashboard from '@/views/admin/AdminDashboard.vue'
import ChatView from '@/views/chat/ChatView.vue'

const routes = [
  { path: '/', component: ProductList, name: 'home' },
  { path: '/cart', component: CartView, name: 'cart' },
  { path: '/orders', component: OrdersView, name: 'orders' },
  { path: '/product/:id', component: ProductDetail, name: 'product-detail' },
  { path: '/order/:id', component: OrderDetail, name: 'order-detail' },
  { path: '/order/:id/logistics', component: OrderLogistics, name: 'order-logistics' },
  { path: '/wishlist', component: WishlistView, name: 'wishlist' },
  { path: '/profile', component: ProfileView, name: 'profile' },
  { path: '/login', component: LoginView, name: 'login' },
  { path: '/register', component: RegisterView, name: 'register' },
  { path: '/profile/edit', component: ProfileEditView, name: 'profile-edit' },
  { path: '/profile/address', component: AddressBookView, name: 'address-book' },
  { path: '/profile/membership', component: MembershipView, name: 'membership' },
  { path: '/membership/plan/:id/detail', component: MembershipDetailView, name: 'membership-detail' },
  { path: '/membership/plan/:id/purchase', component: MembershipPurchaseView, name: 'membership-purchase' },
  { path: '/membership/:level/detail', component: MembershipDetailView, name: 'membership-detail-level' },
  { path: '/membership/:level/purchase', component: MembershipPurchaseView, name: 'membership-purchase-level' },
  { path: '/chat/:productId?', component: ChatView, name: 'chat' },
  { path: '/admin', component: AdminDashboard, name: 'admin' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router

  