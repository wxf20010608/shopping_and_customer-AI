import { defineStore } from "pinia";
import { ref } from "vue";

export const useWishlistStore = defineStore("wishlist", () => {
  const items = ref([]); // product ids

  function toggle(product){
    const id = typeof product === "number" ? product : product?.id;
    if (id == null) return;
    const idx = items.value.indexOf(id);
    if (idx >= 0) items.value.splice(idx, 1);
    else items.value.push(id);
  }

  function has(product){
    const id = typeof product === "number" ? product : product?.id;
    return items.value.includes(id);
  }

  return { items, toggle, has };
});