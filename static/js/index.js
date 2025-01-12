// Lấy điểm số hiện tại của các fighter từ server (giả định có API)
const fetchScores = async () => {
  try {
    const response = await fetch("/api/score", { method: "GET" });
    if (!response.ok) {
      throw new Error("Failed to fetch scores");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
};

const fetchTimer = async () => {
  try {
    const response = await fetch("/api/timer", { method: "GET" });
    if (!response.ok) {
      throw new Error("Failed to fetch scores");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
};
// Cập nhật điểm số mới cho các fighter lên server (giả định có API)
const updateScores = async (newScores) => {
  try {
    const response = await fetch("/api/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newScores),
    });
    if (!response.ok) {
      throw new Error("Failed to update scores");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
};

// Chức năng thêm điểm cho fighter
const addPoints = async (fighter, points) => {
  // Cập nhật điểm mới lên server
  await updateScores({ [fighter]: points });
};

let timerInterval = null;
const startCountdown = async () => {
  const timer = await fetchTimer();
  let endTime = timer.end_time;

  const countdownElement = document.getElementById("countdown-timer");

  // Lấy thời gian hiện tại
  const now = dayjs();

  // Tính khoảng cách giữa thời gian kết thúc và thời gian hiện tại (tính bằng giây)
  let totalSeconds = dayjs(endTime).diff(now, 'second');

  if (totalSeconds > 0) {
    // Tính phút và giây
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    // Hiển thị thời gian lên giao diện
    countdownElement.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

    // Giảm thời gian còn lại
    totalSeconds--;
  } else {
    // Khi hết thời gian, dừng bộ đếm
    clearInterval(timerInterval);
    countdownElement.textContent = "00:00";
  }



};


startCountdown();
setInterval(startCountdown, 1000);

// Lấy và hiển thị điểm số ban đầu khi trang được tải


setInterval(async () => {
  const fingters = await fetchScores();

  // Cập nhật điểm cho tất cả các phần tử có class 'fighter1-score'
  document.querySelectorAll(".fighter1-score").forEach(element => {
    element.textContent = fingters.fighter1_score;
  });

  // Cập nhật điểm cho tất cả các phần tử có class 'fighter2-score'
  document.querySelectorAll(".fighter2-score").forEach(element => {
    element.textContent = fingters.fighter2_score;
  });

  document.querySelectorAll(".fighter1-name").forEach(element => {
    element.textContent = fingters.fighter1_name;
  });
  document.querySelectorAll(".fighter2-name").forEach(element => {
    element.textContent = fingters.fighter2_name;
  });

  //   {
  //   "fighter1_name": "",
  //     "fighter1_score": 0,
  //       "fighter2_name": "",
  //         "fighter2_score": 0
  // }


}, 600);
