// Example Zustand store for in-progress, multi-step form state.
// Reserved for flows like Deviation Management (M7) that span several
// screens — server state itself stays in TanStack Query, not here.
// See architecture doc Section 5.1.

import { create } from "zustand";

interface DeviationFlowState {
  dcNo: string | null;
  expectedQty: number | null;
  actualQty: number | null;
  setDcNo: (dcNo: string) => void;
  setQuantities: (expected: number, actual: number) => void;
  reset: () => void;
}

export const useDeviationFlowStore = create<DeviationFlowState>((set) => ({
  dcNo: null,
  expectedQty: null,
  actualQty: null,
  setDcNo: (dcNo) => set({ dcNo }),
  setQuantities: (expectedQty, actualQty) => set({ expectedQty, actualQty }),
  reset: () => set({ dcNo: null, expectedQty: null, actualQty: null }),
}));
