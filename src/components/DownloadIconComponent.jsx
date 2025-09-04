```jsx src/components/DownloadIconComponent.jsx
import React from 'react';

const DownloadIconComponent = () => {
  return (
    <div className="relative w-full h-full">
      <div className="absolute top-0 right-0">
        <button className="p-2 rounded-full bg-gray-200 hover:bg-gray-300">
          <svg
            version="1.1"
            xmlns="http://www.w3.org/2000/svg"
            xmlns:xlink="http://www.w3.org/1999/xlink"
            x="0px"
            y="0px"
            viewBox="0 0 512 512"
            enable-background="new 0 0 512 512"
            xml:space="preserve"
            className="h-6 w-6"
          >
            <path
              d="M416,199.5h-91.4V64H187.4v135.5H96l160,158.1L416,199.5z M96,402.8V448h320v-45.2H96z"
              fill="currentColor"
            />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default DownloadIconComponent;
```
            <path
              d="M240 419.42L191.98 371l-22.61 23L256 480l86.63-86l-22.61-23L272 419.42V352h-32v67.42z"
              fill="currentColor"
            />
          </svg>
        </button>
      </div>
    </div>
```