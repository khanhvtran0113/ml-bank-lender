import React from "react";
import { Flex } from "@tremor/react";

export const LoadingSpinner = React.memo(() => {
  return (
    <Flex
      justifyContent="center"
      alignItems="center"
      style={{
        height: "100vh",
      }}
    >
      <div className="relative">
        {/* Spinner Circle with Arrow */}
        <div className="animate-spin border-4 border-t-4 border-blue-500 border-solid rounded-full w-16 h-16 flex justify-center items-center">
          {/* Arrow inside the spinner */}
          <div className="absolute text-blue-500 font-bold text-xl transform rotate-90">
            ↻
          </div>
        </div>
      </div>
    </Flex>
  );
});
