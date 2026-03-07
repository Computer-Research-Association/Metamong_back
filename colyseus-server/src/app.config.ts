import config from "@colyseus/tools";
import { monitor } from "@colyseus/monitor";
import { playground } from "@colyseus/playground";

/**
 * Import your Room files
 */

export const ServerGlobal = {
    publicKey: {
        key: "",
        algorithm: ""
    }
};

import { MyRoom } from "./rooms/MyRoom";

export default config({

    initializeGameServer: (gameServer) => {
        /**
         * Define your room handlers:
         */
        //맨 처음 stateful 서버 시작될 때, api, env, pem 등으로부터 server의 public key를 가져올 것
        try {
            console.log("requesting public-key from stateless server");
            const response = await axios.get("http://192.168.29.134:8000/api/auth/key");
            
            // API 응답 구조에 맞춰 수정
            ServerGlobal.publicKey = response.data; 
            ``
            console.log("public-key loaded");
            console.log(ServerGlobal.publicKey.key);
        } catch (error) {
            console.error("failed to load public-key");
            process.exit(1); 
        }
        gameServer.define('my_room', MyRoom);

    },

    initializeExpress: (app) => {
        /**
         * Bind your custom express routes here:
         * Read more: https://expressjs.com/en/starter/basic-routing.html
         */
        app.get("/hello_world", (req, res) => {
            res.send("It's time to kick ass and chew bubblegum!");
        });

        /**
         * Use @colyseus/playground
         * (It is not recommended to expose this route in a production environment)
         */
        if (process.env.NODE_ENV !== "production") {
            app.use("/", playground());
        }

        /**
         * Use @colyseus/monitor
         * It is recommended to protect this route with a password
         * Read more: https://docs.colyseus.io/tools/monitor/#restrict-access-to-the-panel-using-a-password
         */
        app.use("/monitor", monitor());
    },


    beforeListen: () => {
        /**
         * Before before gameServer.listen() is called.
         */
    }
});
