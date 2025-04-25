// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBFT3jOKSyR_xeJO0rIymMPVFmGsAQ83F0",
  authDomain: "zelopack-industria.firebaseapp.com",
  projectId: "zelopack-industria",
  storageBucket: "zelopack-industria.firebasestorage.app",
  messagingSenderId: "993227513134",
  appId: "1:993227513134:web:f03edbada0110b07fa6ebf",
  measurementId: "G-42RS8TZHZH"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

// Export the Firebase instances if needed
export { app, analytics };