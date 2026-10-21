import { createContext, useContext } from "react";

export type UxVersion = 1 | 2;
export const UxContext = createContext<UxVersion>(1);
export const useUxVersion = () => useContext(UxContext);

