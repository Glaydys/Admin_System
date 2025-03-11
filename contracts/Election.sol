// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Election {
    struct Candidate {
        uint id;
        string name;
        string dob; 
        string gender; 
        string nationality; 
        string ethnicity; 
        string religion; 
        string hometown; 
        string currentResidence; 
        string occupation; 
        string workplace; 
        bool isApproved; 
    }

    struct ElectionDetails {
        uint id;
        string name; 
        string region; 
        uint startTime; 
        uint endTime; 
        mapping(uint => Candidate) candidates; 
        uint candidateCount;
    }

    mapping(uint => ElectionDetails) public elections; 
    uint public electionCount; 

    event ElectionCreated(uint id, string name, string region, uint startTime, uint endTime);
    event CandidateAdded(uint electionId, uint candidateId, string name);

    // Tạo cuộc bầu cử
    function createElection(string memory _name, string memory _region, uint _startTime, uint _endTime) public {
        require(_endTime > _startTime, unicode"Thời gian kết thúc phải lớn hơn thời gian bắt đầu");

        electionCount++;
        ElectionDetails storage newElection = elections[electionCount];
        newElection.id = electionCount;
        newElection.name = _name;
        newElection.region = _region;
        newElection.startTime = _startTime;
        newElection.endTime = _endTime;
        newElection.candidateCount = 0;

        emit ElectionCreated(electionCount, _name, _region, _startTime, _endTime);
    }

    // Thêm ứng viên vào cuộc bầu cử
    function addCandidate(
        uint _electionId,
        string memory _name,
        string memory _dob,
        string memory _gender,
        string memory _nationality,
        string memory _ethnicity,
        string memory _religion,
        string memory _hometown,
        string memory _currentResidence,
        string memory _occupation,
        string memory _workplace
    ) public {
        ElectionDetails storage election = elections[_electionId];
        require(election.id != 0, unicode"Cuộc bầu cử không tồn tại");

        election.candidateCount++;
        uint candidateId = election.candidateCount;

        election.candidates[candidateId] = Candidate(
            candidateId,
            _name,
            _dob,
            _gender,
            _nationality,
            _ethnicity,
            _religion,
            _hometown,
            _currentResidence,
            _occupation,
            _workplace,
            false // Mặc định chưa được phê duyệt
        );

        emit CandidateAdded(_electionId, candidateId, _name);
    }


    function approveCandidate(uint _electionId, uint _candidateId) public {
        ElectionDetails storage election = elections[_electionId];
        require(election.id != 0, unicode"Cuộc bầu cử không tồn tại");
        require(_candidateId > 0 && _candidateId <= election.candidateCount, unicode"ID ứng viên không hợp lệ");

        election.candidates[_candidateId].isApproved = true;
    }

    // Lấy thông tin cuộc bầu cử
    function getElection(uint _electionId)
        public
        view
        returns (
            string memory name,
            string memory region,
            uint startTime,
            uint endTime,
            uint candidateCount
        )
    {
        ElectionDetails storage election = elections[_electionId];
        require(election.id != 0, unicode"Cuộc bầu cử không tồn tại");

        return (
            election.name,
            election.region,
            election.startTime,
            election.endTime,
            election.candidateCount
        );
    }

    // Lấy thông tin ứng viên
    function getCandidate(uint _electionId, uint _candidateId)
        public
        view
        returns (
            string memory name,
            string memory dob,
            string memory gender,
            string memory nationality,
            string memory ethnicity,
            string memory religion,
            string memory hometown,
            string memory currentResidence,
            string memory occupation,
            string memory workplace,
            bool isApproved
        )
    {
        ElectionDetails storage election = elections[_electionId];
        require(election.id != 0, unicode"Cuộc bầu cử không tồn tại");
        require(_candidateId > 0 && _candidateId <= election.candidateCount, unicode"ID ứng viên không hợp lệ");

        Candidate storage candidate = election.candidates[_candidateId];
        return (
            candidate.name,
            candidate.dob,
            candidate.gender,
            candidate.nationality,
            candidate.ethnicity,
            candidate.religion,
            candidate.hometown,
            candidate.currentResidence,
            candidate.occupation,
            candidate.workplace,
            candidate.isApproved
        );
    }
}
