
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

// Xử lý file Excel và hiển thị dữ liệu
const handleFileUpload = (event) => {
  const file = event.target.files[0];
  if (file && file.name.endsWith(".xlsx")) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: "array" });
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const jsonData = XLSX.utils.sheet_to_json(sheet);

      displayFighterData(jsonData);
    };
    reader.readAsArrayBuffer(file);
  } else {
    alert("Please upload a valid .xlsx file.");
  }
};

// Hiển thị dữ liệu võ sĩ từ file Excel lên bảng
// Function to render the table dynamically
const displayFighterData = (data) => {
  const tableBody = document.querySelector("#fighterData tbody");
  tableBody.innerHTML = "";  // Clear previous rows

  data.forEach((row, index) => {
    const tr = document.createElement("tr");
    tr.classList.add("hover:bg-gray-100");
    tr.classList.add("hover:text-black");

    tr.innerHTML = `
        <td id="fighter1-name-${index}" class="cursor-pointer px-4 py-2" onclick="selectFighter('fighter1', ${index})">${row['Vosi1']}</td>
        <td id="fighter1-team-${index}" class="px-4 py-2">${row['Doi']}</td>
        <td id="fighter2-name-${index}" class="cursor-pointer px-4 py-2" onclick="selectFighter('fighter2', ${index})">${row['Vosi2']}</td>
        <td id="fighter2-team-${index}" class="px-4 py-2">${row['Doi']}</td>
        <td id="fighter-weight-class-${index}" class="px-4 py-2">${row['HangCan']}</td>
        <td id="fighter-round-${index}" class="px-4 py-2">${row['Vong']}</td>
      
       <td class="px-4 py-2 cursor-pointer flex items-center justify-center relative">
        <label for="fighter-check-${index}" class="flex cursor-pointer h-[40px] bg-blue-500 w-full items-center space-x-2 absolute top-0 left-0 flex items-center justify-center">
          <input type="radio" name="fighter-check" id="fighter-check-${index}" onchange="setFighter(${index})" class="form-radio h-5 cursor-pointer w-5 text-blue-500 focus:ring-2 focus:ring-blue-300">
        </label>
      </td>
        `;

    tableBody.appendChild(tr);
  });

  // Show the table
  document.getElementById("fighterData").classList.remove("hidden");
};

// Function to handle the checkbox toggle and capture points
const setFighter = (index) => {
  const checkbox = document.querySelector(`#fighter-check`);

  // Get references to the other elements for the selected fighter
  const fighterName1 = document.querySelector(`#fighter1-name-${index}`).textContent;  // For non-input fields, use textContent
  const fighterTeam1 = document.querySelector(`#fighter1-team-${index}`).textContent;
  // Get references to the other elements for the selected fighter
  const fighterName2 = document.querySelector(`#fighter2-name-${index}`).textContent;  // For non-input fields, use textContent
  const fighterTeam2 = document.querySelector(`#fighter2-team-${index}`).textContent;
  const weightClass = document.querySelector(`#fighter-weight-class-${index}`).textContent;
  const round = document.querySelector(`#fighter-round-${index}`).textContent;



  fetch('/api/update_current_fighter', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      fighter1_name: fighterName1,
      fighter1_team: fighterTeam1,
      fighter2_name: fighterName2,
      fighter2_team: fighterTeam2,
      weight_class: weightClass,
      round: round,
      fighter1_score: 0,
      fighter2_score: 0
    })
  })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error updating current fighter:', error));

};
// Chức năng chọn võ sĩ

// Chức năng thay đổi trạng thái checkbox và tính điểm
// Function to update the current fighter's data in your system (e.g., backend)
const updateCurrentFighter = (name, team, weightClass, round, points) => {
  console.log(`Updating current fighter with the following info:`);
  console.log(`Name: ${name}, Team: ${team}, Weight Class: ${weightClass}, Round: ${round}, Points: ${points}`);

  // Example of an API request to update current fighter data

};

const startFighter = (round) => {
  console.log(`Starting the fight...`);  // Log the start of the fight

  // Tạo đối tượng dữ liệu cho yêu cầu API
  const data = {
    round: round,
    start_time: dayjs(),
    end_time: dayjs().add(2.5, 'minute')
  };

  // Gọi API /api/start_fight
  fetch('/api/start_fight', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data), // Gửi dữ liệu qua body yêu cầu
  })
    .then((response) => response.json())
    .then((data) => {
      // Xử lý kết quả trả về từ API
      console.log('Fight started:', data.message);
      console.log('Start Time:', data.start_time);
      console.log('End Time:', data.end_time);
    })
    .catch((error) => {
      console.error('Error starting the fight:', error);
    });
};

// Function to reset the current fighter's data (if necessary)
const resetCurrentFighter = () => {
  console.log(`Resetting current fighter data...`);

  // Example of an API request to reset current fighter data
  fetch('/api/reset_current_fighter', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error('Error resetting current fighter:', error));
};

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
// Lấy và hiển thị điểm số ban đầu khi trang được tải
setInterval(async () => {
  const scores = await fetchScores();
  document.querySelectorAll(".fighter1-score").forEach(element => {
    element.textContent = scores.fighter1_score;
  });
  document.querySelectorAll(".fighter2-score").forEach(element => {
    element.textContent = scores.fighter2_score;
  });
}, 300);