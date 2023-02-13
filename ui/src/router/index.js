import { createRouter, createWebHistory } from "vue-router";
import NProgress from "nprogress/nprogress";
import NimPlantDetails from "../views/NimPlant/Details.vue";
import NimPlantConsole from "../views/NimPlant/Console.vue";
import NimPlants from "../views/NimPlants.vue";
import Server from "../views/Server.vue";
import ServerConsole from "../views/Server/Console.vue";
import ServerExit from "../views/Server/Exit.vue";
import store from "../store";

const routes = [
    {
        path: "/",
        redirect: "/nimplants",
    },
    {
        path: "/nimplants",
        name: "nimplants",
        component: NimPlants,
        async beforeEnter(routeTo, routeFrom, next) {
            await store.dispatch('fetchNimPlants')

            next()
        },
    },
    {
        path: "/nimplants/:guid",
        name: "nimplant",
        redirect: { name: "nimplant.console"},
    },
    {
        path: "/nimplants/:guid/details",
        name: "nimplant.details",
        component: NimPlantDetails,
        async beforeEnter(routeTo, routeFrom, next) {
            await store.dispatch('fetchNimPlant', routeTo.params.guid)

            next();
        },
    },
    {
        path: "/nimplants/:guid/console",
        name: "nimplant.console",
        component: NimPlantConsole,
        async beforeEnter(routeTo, routeFrom, next) {
            await store.dispatch('fetchNimPlant', routeTo.params.guid)
            await store.dispatch('fetchNimPlantConsole', routeTo.params.guid)

            next();
        },
    },
    {
        path: "/server",
        name: "server",
        component: Server,
        async beforeEnter(routeTo, routeFrom, next) {
            if (! store.getters.server) {
                await store.dispatch('fetchServer')
            }

            next();
        },
    },
    {
        path: "/server/console",
        name: "server.console",
        component: ServerConsole,
        async beforeEnter(routeTo, routeFrom, next) {
            if (! store.getters.server) {
                await store.dispatch('fetchServer')
            }

            if (! store.getters.serverConsole) {
                await store.dispatch('fetchServerConsole')
            }

            next();
        },
    },
    {
        path: "/server/exit",
        name: "server.exit",
        component: ServerExit,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach(async (routeTo, routeFrom, next) => {
    NProgress.start();

    if (store.getters.server == null) {
        await store.dispatch('fetchServer')
    }

    next();
});

router.afterEach(() => {
    NProgress.done();
});

export default router;
