# Research: Simplifying Daily Hostel Gate Record-Keeping

## Problem Statement

The hostel houses approximately 500 girls and currently relies on a manual register to record student entry and exit movements.

According to Babita Kumari, a security guard responsible for the hostel gates, reviewing the records around the 9:30 PM deadline is time-consuming.

Missing entries and inconsistent student details make it difficult to identify records that need attention and report them to the warden.

Analysing gate activity manually also makes it harder to identify busy entry and exit periods that may require additional attention from security staff.

I will build a lightweight web application using Python and Streamlit that reads a CSV file containing gate activity records, allows the user to select a date and return cutoff time, flags records requiring verification, identifies peak entry and exit periods, and generates useful summaries to support daily monitoring.

## Existing Solutions

### 1. Integrated Hostel Management System

**Source:** [Design and Implementation of an Integrated Hostel Management System with Role-Based Access for Students and Wardens](https://tmg.chitkara.edu.in/2025/design-and-implementation-of-an-integrated-hostel-management-system-with-role-based-access-for-students-and-wardens/)

**What it offers:**

The paper describes a web-based hostel management system with separate student and warden functionality, including gate-pass requests, student record management, and communication features.

**Why it is not the immediate solution for Babita:**

It addresses several hostel administration activities, whereas Babita needs a small tool focused on reviewing daily gate records and identifying late or incomplete records. A larger integrated system would be beyond the scope of this one-day prototype.

**Important limitation:**

This does not prove that an integrated system would be unsuitable for the hostel. The proposed tool is deliberately narrower and does not assume that the college will adopt a new official system.

### 2. Web-Based Hostel Management System

**Source:** [Hostel Management System — IJRASET](https://www.ijraset.com/research-paper/hostel-management-system-)

**What it offers:**

The paper describes a web-based system for hostel administration, including student records, room allocation, fee management, complaint handling, and centralized data storage.

**Why it is not the immediate solution for Babita:**

Its scope covers multiple administrative processes. Babita's immediate problem is more specific: analysing daily gate records, identifying records that need verification, reviewing returns against a user-selected cutoff time, and understanding peak entry and exit periods without repeatedly checking the entire register.

**Important limitation:**

The paper discusses a broader hostel management approach; it does not establish whether that system or its workflow would suit Babita's day-to-day constraints.

## Sources Read: Notes

### Source 1: Design and Implementation of an Integrated Hostel Management System with Role-Based Access for Students and Wardens

1. The paper identifies paper-based hostel processes, including gate passes and handwritten records, as sources of inefficiency.
2. It describes a web application with student and warden modules, including gate-pass requests and student record management.
3. It provides an example of a broader digital hostel system against which a smaller, guard-focused tool can be scoped.

### Source 2: Hostel Management System — IJRASET

1. The paper discusses difficulties associated with manual hostel administration, including record errors, redundancy, and time-consuming processes.
2. It proposes a web-based application with centralized data storage and modules for different hostel management activities.
3. It provides a comparison with broader digital record-management systems and supports investigating a more narrowly scoped solution for the guard's daily workflow.

## Proposed Approach

The prototype will use Python, Streamlit, and Pandas to analyse a CSV file containing gate activity records.

The user will be able to select a date and cutoff time rather than relying on a hardcoded deadline. The application will identify records requiring verification, analyse entry and exit activity by time period, and highlight busy periods that may warrant a review of guard deployment.

The prototype will be limited to the data provided. Missing records will not automatically be treated as proof that a student is absent or has violated hostel rules, and staffing suggestions will be presented as indicators for review rather than definitive recommendations.
